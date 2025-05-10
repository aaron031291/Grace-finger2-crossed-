from fastapi import FastAPI, Depends, HTTPException, WebSocket, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import Dict, List, Optional
import jwt
import redis
import json
import logging
from datetime import datetime, timedelta
from functools import lru_cache
import re

# Optional fallback if display_config.py is missing
class DisplayConfig(BaseModel):
    theme: str = "dark"
    layout: str = "grid"
    show_logs: bool = True

active_config = DisplayConfig()

# Configuration
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

redis_pool = redis.ConnectionPool(host='redis', port=6379, db=0)
SECRET_KEY = "grace_enterprise_2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

logger = logging.getLogger("grace-dashboard")
logger.setLevel(logging.INFO)

# Models
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
        allowed_commands = {"trigger_audit", "force_rollback", "module_restart"}
        if v not in allowed_commands:
            raise ValueError(f"Invalid command. Allowed: {allowed_commands}")
        return v

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

@lru_cache()
def get_redis():
    try:
        return redis.Redis(connection_pool=redis_pool)
    except redis.RedisError as e:
        logger.critical(f"Redis connection failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Cache unavailable")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(**payload)
    except jwt.PyJWTError:
        raise credentials_exception

    user = User(username=username, roles=payload.get("roles", ["viewer"]))
    return user

# Endpoints
@app.post("/token", response_model=Dict[str, str])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "grace2025":
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    access_token = create_access_token({"sub": form_data.username, "roles": ["admin"]})
    refresh_token = create_refresh_token({"sub": form_data.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
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
        await pubsub.subscribe("cognitive_map_updates")
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"].decode())
    except Exception as e:
        logger.error(f"WS error: {str(e)}")
    finally:
        await pubsub.unsubscribe()

@app.get("/module-health", response_model=Dict[str, Dict])
async def get_module_health(user: User = Depends(get_current_user)):
    redis_conn = get_redis()
    cached = redis_conn.get("module_health")
    if cached:
        return json.loads(cached)
    health_data = {
        "kpis": {"uptime_percent": 99.95, "error_rate": 0.2},
        "diagnostics": {"last_check": datetime.utcnow().isoformat()},
        "modules": ["core", "diagnostics", "audit"]
    }
    redis_conn.setex("module_health", 300, json.dumps(health_data))
    return health_data

@app.post("/execute-command")
async def execute_command(cmd: CommandExecution, user: User = Depends(get_current_user)):
    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    result = f"Executed {cmd.command} with params {cmd.parameters}"
    logger.info(f"Command executed by {user.username}: {result}")
    return {"status": "success", "result": result}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"X-Grace-Error": "true"}
    )

@app.get("/display-config")
async def get_display_config():
    return active_config.dict()

@app.post("/update-config")
async def update_config(new_config: dict):
    global active_config
    active_config = DisplayConfig(**new_config)
    return {"status": "updated"}

# Routers
from interface_router import router as interface_router
from interface_control_router import router as interface_control_router
from layout_controller import router as layout_router

app.include_router(interface_router)
app.include_router(interface_control_router)
app.include_router(layout_router)

# Token helpers
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
