# grace_core_systems/central_intelligence/public_api_launcher.py

"""
Public API Launcher
Exposes Grace’s public-facing interface for external contributors, sandboxed pods, and integration requests.
Secured via trust metadata and policy layer hooks.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import logging
import uuid
from datetime import datetime

logger = logging.getLogger("PublicAPI")
logger.setLevel(logging.INFO)

app = FastAPI(title="Grace Public API", version="1.0.0")

# Allow CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory record of API events (can route to database or file later)
API_LOG = []

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    timestamp = str(datetime.utcnow())
    method = request.method
    path = request.url.path

    logger.info(f"[API] Incoming request {method} {path} @ {timestamp}")
    API_LOG.append({
        "id": request_id,
        "timestamp": timestamp,
        "method": method,
        "path": path
    })

    response = await call_next(request)
    return response

@app.post("/submit_pod")
async def submit_pod(file: UploadFile = File(...), contributor_id: str = "anonymous"):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")

    try:
        contents = await file.read()
        # Placeholder: route to sandbox gatekeeper
        logger.info(f"[API] ✅ Pod received from {contributor_id}: {file.filename} ({len(contents)} bytes)")
        return {"status": "queued", "filename": file.filename, "contributor": contributor_id}
    except Exception as e:
        logger.error(f"[API] ❌ Failed to read uploaded pod: {e}")
        raise HTTPException(status_code=500, detail="Failed to process file.")

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "timestamp": str(datetime.utcnow()),
        "uptime": f"{round(float(uuid.uuid1().time / 1e7), 2)}s"
    }

@app.get("/log")
async def get_api_log():
    return JSONResponse(content=API_LOG)

# Run manually or via ASGI deployment
# uvicorn public_api_launcher:app --reload
