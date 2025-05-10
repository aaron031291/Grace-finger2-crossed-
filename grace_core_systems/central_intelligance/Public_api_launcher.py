"""
Public API Launcher
Exposes Grace’s public interface for pod submission, NLP interpretation, and health/status checks.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime

from grace_core_systems.language_layer import nlp_gateway

logger = logging.getLogger("PublicAPI")
logger.setLevel(logging.INFO)

app = FastAPI(title="Grace Public API", version="1.0.0")

# Allow CORS for integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API request log
API_LOG = []

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    timestamp = str(datetime.utcnow())
    method = request.method
    path = request.url.path

    logger.info(f"[API] Request {method} {path} @ {timestamp}")
    API_LOG.append({
        "id": request_id,
        "timestamp": timestamp,
        "method": method,
        "path": path
    })

    response = await call_next(request)
    return response

# Upload endpoint for pods or modules
@app.post("/submit_pod")
async def submit_pod(file: UploadFile = File(...), contributor_id: str = "anonymous"):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")

    try:
        contents = await file.read()
        logger.info(f"[API] ✅ Pod received from {contributor_id}: {file.filename} ({len(contents)} bytes)")
        return {"status": "queued", "filename": file.filename, "contributor": contributor_id}
    except Exception as e:
        logger.error(f"[API] ❌ Failed to read uploaded pod: {e}")
        raise HTTPException(status_code=500, detail="Failed to process file.")

# NLP input endpoint
class NLPRequest(BaseModel):
    message: str

@app.post("/nlp")
async def process_nlp(request: NLPRequest):
    parsed = nlp_gateway.parse_input(request.message)
    result = nlp_gateway.route_intent(parsed)
    return {"response": result}

# System health ping
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "timestamp": str(datetime.utcnow()),
        "uptime": f"{round(float(uuid.uuid1().time / 1e7), 2)}s"
    }

# API request log retrieval
@app.get("/log")
async def get_api_log():
    return JSONResponse(content=API_LOG)
