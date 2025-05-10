# Placeholder for NLP gateway
"""
NLP Gateway
Handles natural language input, parses intent, routes to Grace's cognitive modules.
Supports LLM proxy, offline fallback, and direct command recognition.
"""

import logging
from typing import Dict

logger = logging.getLogger("NLP-Gateway")
logger.setLevel(logging.INFO)

# Sample intent registry (placeholder for future model)
INTENT_MAP = {
    "status": "check_system_health",
    "modules": "list_loaded_modules",
    "ethics": "run_ethics_audit",
    "memory": "query_fusion_memory",
    "help": "display_help_menu"
}

def parse_input(message: str) -> Dict:
    """
    Parse incoming text to extract intent and route information.
    """
    logger.info(f"[NLP] Received: {message}")

    cleaned = message.lower().strip()

    for keyword, intent in INTENT_MAP.items():
        if keyword in cleaned:
            logger.info(f"[NLP] Matched intent: {intent}")
            return {
                "status": "matched",
                "intent": intent,
                "raw": message
            }

    logger.warning("[NLP] No match found. Flagging for fallback.")
    return {
        "status": "unrecognized",
        "intent": "fallback_reroute",
        "raw": message
    }

def route_intent(parsed: Dict) -> str:
    """
    Route parsed intent to a subsystem or return fallback.
    """
    intent = parsed.get("intent")

    if intent == "check_system_health":
        return "System status: ✅ All modules stable."

    elif intent == "list_loaded_modules":
        return "Modules: Grace Boot, Ethics Core, Telemetry, Evolution Layer..."

    elif intent == "run_ethics_audit":
        return "Launching ethics compliance scan..."

    elif intent == "query_fusion_memory":
        return "Fusion Memory log not yet connected."

    elif intent == "display_help_menu":
        return "Available commands: status, modules, ethics, memory, help."

    elif intent == "fallback_reroute":
        return f"Sorry, I didn't understand: \"{parsed.get('raw')}\""

    return "Unknown command routing error."

# Manual test
if __name__ == "__main__":
    sample = "What’s the system status?"
    parsed = parse_input(sample)
    response = route_intent(parsed)
    print(response)
