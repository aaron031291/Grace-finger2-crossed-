# grace_core_systems/main.py

import sys
import logging
from fastapi import FastAPI
from grace_core_systems.central_intelligence import core
from grace_core_systems.GUI.dashboard.backend import dashboard_app
from grace_core_systems.GUI.display_config import active_config

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Launching Grace v1-core-stable...")

# Initialize FastAPI app
app = FastAPI(title="Grace Core Systems", version="v1-core-stable")

# Mount dashboard
app.mount("/dashboard", dashboard_app)

# Load system configuration
logger.info(f"Active display configuration: {active_config}")

# Boot up Grace's central intelligence core
@app.on_event("startup")
async def boot_grace_core():
    logger.info("Boot sequence initiated.")
    try:
        await core.initialize_core()
        logger.info("Grace Core initialized successfully.")
    except Exception as e:
        logger.error(f"Error during core boot: {e}")
        raise

# Optional root ping
@app.get("/")
def index():
    return {
        "status": "Grace online",
        "version": "v1-core-stable"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
