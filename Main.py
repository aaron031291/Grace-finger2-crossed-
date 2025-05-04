# grace_core_systems/main.py

import sys
import logging
from fastapi import FastAPI

from grace_core_systems.central_intelligence import core
from grace_core_systems.GUI.dashboard.backend import dashboard_app
from grace_core_systems.GUI.display_config import active_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
logger.info("Launching Grace v1-core-stable...")

# FastAPI initialization
app = FastAPI(
    title="Grace Core Systems",
    version="v1-core-stable",
    description="AI Sovereignty. Ethical Intelligence. Modular Autonomy."
)

# Mount GUI dashboard
app.mount("/dashboard", dashboard_app)

# Display current visual configuration
logger.info(f"Display config: {active_config}")

# Core boot sequence
@app.on_event("startup")
async def launch_grace():
    logger.info("Booting Grace Central Intelligence Core...")
    try:
        await core.initialize_core()
        logger.info("Grace Core initialized successfully.")
    except Exception as error:
        logger.error(f"Core boot failure: {error}")
        raise

# Root ping
@app.get("/")
def index():
    return {
        "status": "Grace online",
        "version": "v1-core-stable"
    }

# Local test mode
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("grace_core_systems.main:app", host="0.0.0.0", port=8000, reload=True)
