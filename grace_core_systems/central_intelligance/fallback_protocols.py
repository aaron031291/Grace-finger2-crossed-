# grace_core_systems/central_intelligence/fallback_protocols.py

"""
Fallback Protocols
Defines Grace’s emergency response systems under critical degradation, ethics breach, or module failure.
"""

import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger("FallbackProtocols")
logger.setLevel(logging.INFO)

FALLBACK_LOG = []

# Define global fallback conditions
CRITICAL_MODULES = {"unified_logic", "ethics_bot", "memory_controller", "interface_router"}

# Registry for modules currently under fallback
FALLBACK_STATE = {}

def trigger_fallback(module_name: str, reason: str):
    timestamp = str(datetime.utcnow())
    logger.warning(f"[FALLBACK] ⚠️ Triggered for '{module_name}' | Reason: {reason}")
    
    FALLBACK_STATE[module_name] = {
        "status": "fallback_engaged",
        "reason": reason,
        "timestamp": timestamp
    }

    FALLBACK_LOG.append({
        "module": module_name,
        "reason": reason,
        "timestamp": timestamp
    })

    if module_name in CRITICAL_MODULES:
        escalate_to_parliament(module_name, reason)

def escalate_to_parliament(module: str, issue: str):
    logger.error(f"[ESCALATION] Parliament escalation triggered for critical module: {module}")
    # Optional: route to parliament voting or override path
    # from grace_core_systems.parliament import emergency_vote
    # emergency_vote(module, issue)

def is_in_fallback(module_name: str) -> bool:
    return module_name in FALLBACK_STATE and FALLBACK_STATE[module_name]["status"] == "fallback_engaged"

def clear_fallback(module_name: str):
    if module_name in FALLBACK_STATE:
        logger.info(f"[FALLBACK] ✅ Cleared fallback for module: {module_name}")
        FALLBACK_STATE[module_name]["status"] = "resolved"

def get_fallback_status() -> Dict[str, Dict]:
    return FALLBACK_STATE

def get_fallback_log() -> List[Dict]:
    return FALLBACK_LOG

# Manual test
if __name__ == "__main__":
    trigger_fallback("ethics_bot", "ethics signature mismatch")
    trigger_fallback("sandbox_gatekeeper", "unexpected contributor injection")
    print(get_fallback_status())
