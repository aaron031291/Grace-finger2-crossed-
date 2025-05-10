from fastapi import FastAPI, Depends, HTTPException, WebSocket, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
from functools import lru_cache
import jwt
import redis
import json
import logging
import os

# Grace startup log
print(f"[Grace Boot] Starting Dashboard at {datetime.utcnow().isoformat()} | Mode: {os.getenv('GRACE_ENV', 'sandbox')}")

# Init app
app = FastAPI()

# Static directory mount
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if not STATIC_DIR.exists():
    raise RuntimeError(f"[BOOT ERROR] Static directory not found: {STATIC_DIR}")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Env config
SECRET_KEY = os.environ.get("SECRET_KEY", "grace_default_key")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Redis pool
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Logging
logger = logging.getLogger("grace-dashboard")
logger.setLevel(logging.INFO)

# Models
class DisplayConfig(BaseModel):
    theme: str = "dark"
    layout: str = "grid"
    show_logs: bool = True

active_config = DisplayConfig()

class User(BaseModel):
    username: str
    roles: List[str] = ["viewer"]
    disabled: bool = False

class TokenData(BaseModel):
    username: Optional[str] = None
    token_type: Optional[str] = None

class CognitiveMapRequest(BaseModel):
    depth: int = 3
    include_memory: bool = False

    @validator('depth')
    def validate_depth(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Depth must be 1–5")
        return v

class CommandExecution(BaseModel):
    command: str
    parameters: Dict[str, str]

    @validator('command')
    def validate_command(cls, v):
        allowed = {"trigger_audit", "force_rollback", "module_restart"}
        if v not in allowed:
            raise ValueError(f"Invalid command. Allowed: {allowed}")
        return v

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

@lru_cache()
def get_redis():
    try:
        return redis.Redis(connection_pool=redis_pool)
    except redis.RedisError as e:
        logger.critical(f"[REDIS ERROR] {str(e)}")
        raise HTTPException(status_code=503, detail="Redis unavailable")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return User(username=username, roles=payload.get("roles", ["viewer"]))
    except jwt.PyJWTError as e:
        logger.warning(f"[AUTH] JWT decode failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
def root():
    return {"message": "Grace is alive", "timestamp": datetime.utcnow().isoformat()}

@app.post("/token", response_model=Dict[str, str])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "grace2025":
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    return {
        "access_token": create_access_token({"sub": form_data.username, "roles": ["admin"]}),
        "refresh_token": create_refresh_token({"sub": form_data.username}),
        "token_type": "bearer"
    }

@app.websocket("/ws/cognitive-map")
async def cognitive_map_ws(websocket: WebSocket):
    await websocket.accept()
    token = websocket.query_params.get("token")
    user = await get_current_user(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        redis_conn = get_redis()
        pubsub = redis_conn.pubsub()
        pubsub.subscribe("cognitive_map_updates")
        for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"].decode())
    except Exception as e:
        logger.error(f"[WebSocket] {str(e)}")
    finally:
        pubsub.unsubscribe()

@app.get("/module-health", response_model=Dict[str, Dict])
async def get_module_health(user: User = Depends(get_current_user)):
    redis_conn = get_redis()
    cached = redis_conn.get("module_health")
    if cached:
        return json.loads(cached)
    health = {
        "kpis": {"uptime_percent": 99.95, "error_rate": 0.2},
        "diagnostics": {"last_check": datetime.utcnow().isoformat()},
        "modules": ["core", "diagnostics", "audit"]
    }
    redis_conn.setex("module_health", 300, json.dumps(health))
    return health

@app.post("/execute-command")
async def execute_command(cmd: CommandExecution, user: User = Depends(get_current_user)):
    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    logger.info(f"[COMMAND] {user.username} executed {cmd.command} with {cmd.parameters}")
    return {"status": "success", "result": f"Executed {cmd.command}"}

@app.get("/display-config")
async def get_display_config():
    return active_config.dict()

@app.post("/update-config")
async def update_config(new_config: dict):
    global active_config
    active_config = DisplayConfig(**new_config)
    return {"status": "updated"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"[HTTP ERROR] {request.url} | {exc.status_code} | {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"X-Grace-Error": "true"}
    )

# Router stubs (commented out until files are present)
# from interface_router import router as interface_router
# from interface_control_router import router as interface_control_router
# from layout_controller import router as layout_router
# app.include_router(interface_router)
# app.include_router(interface_control_router)
# app.include_router(layout_router)

# Token creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Run locally and in Railway
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("dashboard.backend:app", host="0.0.0.0", port=port, reload=False)
