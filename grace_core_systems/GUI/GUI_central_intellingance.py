from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio
from pydantic import BaseModel

# ========== CORE SETUP ==========
router = APIRouter(
    prefix="/core",
    tags=["central_intelligence"],
    responses={404: {"description": "Endpoint not found"}}
)

logger = logging.getLogger("grace.core")
security_scheme = APIKeyHeader(name="X-GRACE-API-KEY")

# ========== MODELS ==========
class GraceResponse(BaseModel):
    response_id: str
    timestamp: datetime
    input: Optional[Dict[str, Any]]
    output: Dict[str, Any]
    metadata: Dict[str, Any]
    confidence: float = 1.0

class SystemStatus(BaseModel):
    component: str
    status: str
    version: str
    last_heartbeat: datetime

# ========== STATE MANAGEMENT ==========
class CoreState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
            cls._instance.systems = {}
            cls._instance.api_keys = set()
        return cls._instance

# ========== DEPENDENCIES ==========
async def verify_api_key(api_key: str = Depends(security_scheme)):
    state = CoreState()
    if api_key not in state.api_keys:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key

# ========== CORE FUNCTIONS ==========
async def initialize_core():
    """Initialize Grace's central intelligence systems"""
    state = CoreState()
    if state.initialized:
        logger.warning("Core already initialized")
        return
    
    logger.info("Starting Grace Central Intelligence initialization")
    
    # Register core systems
    state.systems = {
        "memory": {"status": "offline", "version": "0.1"},
        "reasoning": {"status": "offline", "version": "0.1"},
        "interface": {"status": "booting", "version": "0.1"},
        "security": {"status": "offline", "version": "0.1"}
    }
    
    # Generate initial API keys
    state.api_keys = {f"grace-key-{uuid.uuid4().hex[:12]}"}
    
    # Simulate system bring-up
    await _bring_up_systems()
    
    state.initialized = True
    logger.info("Grace Central Intelligence fully online")

async def _bring_up_systems():
    """Simulated system initialization sequence"""
    state = CoreState()
    
    # Ordered startup
    systems_order = ["security", "memory", "reasoning", "interface"]
    
    for system in systems_order:
        await asyncio.sleep(0.5)  # Simulate startup delay
        state.systems[system]["status"] = "online"
        state.systems[system]["last_heartbeat"] = datetime.utcnow()
        logger.info(f"{system.capitalize()} subsystem online")
    
    logger.info("All core systems operational")

# ========== API ENDPOINTS ==========
@router.on_event("startup")
async def startup_event():
    await initialize_core()

@router.get("/ping", response_model=GraceResponse)
async def ping(api_key: str = Depends(verify_api_key)):
    """Health check endpoint"""
    state = CoreState()
    return GraceResponse(
        response_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        output={
            "status": "operational",
            "systems": state.systems,
            "message": "Grace central intelligence responding"
        },
        metadata={"api_key": api_key[-6:]},  # Show partial key for verification
        confidence=1.0
    )

@router.post("/query", response_model=GraceResponse)
async def process_query(
    query: Dict[str, Any],
    api_key: str = Depends(verify_api_key),
    timeout: int = 5
):
    """Main query processing endpoint"""
    try:
        # Validate input
        if not query or "input" not in query:
            raise HTTPException(
                status_code=400,
                detail="Invalid query format"
            )
        
        # Process query (simulated)
        processed = await _simulate_processing(query["input"], timeout)
        
        return GraceResponse(
            response_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            input=query,
            output=processed,
            metadata={
                "processing_time": f"{timeout}ms",
                "systems_used": ["memory", "reasoning"]
            },
            confidence=0.95
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal processing error"
        )

@router.get("/systems", response_model=Dict[str, SystemStatus])
async def get_system_status(api_key: str = Depends(verify_api_key)):
    """Get status of all core systems"""
    state = CoreState()
    return {
        name: SystemStatus(
            component=name,
            status=details["status"],
            version=details["version"],
            last_heartbeat=details.get("last_heartbeat", datetime.utcnow())
        )
        for name, details in state.systems.items()
    }

# ========== INTERNAL PROCESSING ==========
async def _simulate_processing(input_data: str, timeout: int) -> Dict:
    """Simulated processing pipeline"""
    # Simulate different processing times
    await asyncio.sleep(min(timeout / 1000, 0.1))
    
    # Simple response transformation
    return {
        "response": f"Processed: {input_data}",
        "analysis": {
            "sentiment": "positive",
            "urgency": 0.3,
            "entities": ["user_input"]
        },
        "suggested_actions": [
            {"action": "memory_store", "confidence": 0.8},
            {"action": "user_followup", "confidence": 0.6}
        ]
    }

# ========== UTILITIES ==========
def generate_api_key() -> str:
    """Generate a new API key and register it"""
    state = CoreState()
    new_key = f"grace-key-{uuid.uuid4().hex[:12]}"
    state.api_keys.add(new_key)
    return new_key

def revoke_api_key(key: str) -> bool:
    """Revoke an existing API key"""
    state = CoreState()
    if key in state.api_keys:
        state.api_keys.remove(key)
        return True
    return False
