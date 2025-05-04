# grace_core_systems/main.py

import sys
import logging
from fastapi import FastAPI
from grace_core_systems.central_intelligence import core
from grace_core_systems.GUI.dashboard.backend import dashboard_app
from grace_core_systems.GUI.display_config import active_config
from grace_core_systems.central_intelligence.core import router as core_router

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
logger.info(">>> Launching Grace v1-core-stable...")

# ========== FASTAPI APP SETUP ==========
app = FastAPI(
    title="Grace Core Systems",
    version="v1-core-stable",
    description="AI Sovereignty. Ethical Intelligence. Modular Autonomy."
)

# ========== GUI DASHBOARD ==========
app.mount("/dashboard", dashboard_app)
logger.info(f">>> Display config loaded: {active_config}")

# ========== STARTUP LOGIC ==========
@app.on_event("startup")
async def startup_event():
    logger.info(">>> Grace Central Intelligence booting...")
    try:
        await core.initialize_core()
        logger.info(">>> Grace Core successfully initialized.")
    except Exception as e:
        logger.error(f"!!! Grace Core startup failed: {e}")
        raise

# ========== ROOT HEALTH PING ==========
@app.get("/")
def root_status():
    return {
        "status": "Grace online",
        "version": "v1-core-stable"
    }

# ========== CENTRAL INTELLIGENCE ROUTER ==========
app.include_router(core_router)

# ========== LOCAL RUNNING INTERFACE ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("grace_core_systems.main:app", host="0.0.0.0", port=8000, reload=True)
