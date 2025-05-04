##############################################
# fallback_manager.py
##############################################

import logging
from datetime import datetime

class FallbackManager:
    @staticmethod
    def escalate_to_human(session_id: str, reason: str):
        logging.warning(f"Escalating session {session_id}: {reason}")
        # Integration point for human interface
        NegotiationState.update_state(session_id, "human_review")

    @staticmethod
    def log_failed_session(session_id: str, reason: str):
        logging.error(f"Failed negotiation {session_id}: {reason}")
        NegotiationState.archive_session(session_id)