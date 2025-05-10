# grace_core_systems/central_intelligence/interface_router.py

"""
Interface Router
Handles inbound I/O from chat, file, test, and live API endpoints.
Dispatches signals to core cognition systems: Unified Logic, Memory, Ethics, and Output.
"""

import logging
from datetime import datetime

# Simulated subsystem imports
from grace_core_systems.central_intelligence import unified_logic
from grace_core_systems.central_intelligence import validator

logger = logging.getLogger("InterfaceRouter")
logger.setLevel(logging.INFO)

# Supported I/O Modes
MODES = ["sandbox", "test", "live"]

def start_sandbox():
    logger.info("[Router] Sandbox mode initiated.")
    run_interface_loop(mode="sandbox")

def start_test():
    logger.info("[Router] Test mode initiated.")
    run_interface_loop(mode="test")

def start_live():
    logger.info("[Router] Live API mode initiated.")
    # This is where you'd start FastAPI/Flask/etc. server routing
    logger.info("[Router] Live API handler not implemented in CLI-only mode.")

def run_interface_loop(mode="sandbox"):
    print(f"[{mode.upper()} MODE] Grace is now listening. Type 'exit' to quit.")
    while True:
        user_input = input(f"[{datetime.utcnow()}] You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("[Router] Grace shutting down interface.")
            break

        try:
            validated = validator.validate_input(user_input)
            response = unified_logic.process(validated)
            print(f"[Grace]: {response}")
        except Exception as e:
            print(f"[Router] ❌ Error processing input: {e}")
            logger.exception("Router exception")

# Optional: CLI entry
if __name__ == "__main__":
    start_sandbox()
