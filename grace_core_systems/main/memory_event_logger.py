##############################
# memory/event_logger.py
##############################

import json
import logging
from datetime import datetime
from typing import Dict, Any
from logging.handlers import RotatingFileHandler

class EventLogger:
    def __init__(self, log_path: str = "memory_events.log"):
        self.logger = logging.getLogger("MemoryEvents")
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Structured event logging with context"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "data": data
        }
        self.logger.info(json.dumps(log_entry))