##############################################
# negotiation_state.py
##############################################

from typing import Dict
import threading

class NegotiationState:
    _sessions = {}
    _lock = threading.Lock()
    
    @classmethod
    def start_session(cls, session_id: str):
        with cls._lock:
            cls._sessions[session_id] = {
                "state": "init",
                "created": datetime.now(),
                "events": []
            }

    @classmethod
    def update_state(cls, session_id: str, new_state: str):
        with cls._lock:
            if session_id in cls._sessions:
                cls._sessions[session_id]["state"] = new_state
                cls._sessions[session_id]["events"].append({
                    "timestamp": datetime.now(),
                    "event": f"state_change:{new_state}"
                })

    @classmethod
    def get_state(cls, session_id: str) -> Dict:
        return cls._sessions.get(session_id, {})