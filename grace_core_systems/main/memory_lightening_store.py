##############################
# memory/lightning_store.py
##############################

import redis
import json
import threading
import time
from typing import Dict, Any
from pydantic import BaseModel
from pathlib import Path

class LightningConfig(BaseModel):
    redis_host: str = "localhost"
    redis_port: int = 6379
    decay_interval: int = 300  # Seconds between decay cycles
    capacity: int = 100000  # Max items in lightning memory

class LightningStore:
    def __init__(self, config: LightningConfig):
        self.conn = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True
        )
        self.decay_thread = threading.Thread(target=self._run_decay)
        self.running = True
        self.decay_interval = config.decay_interval
        
    def push(self, anchor_id: str, data: Dict[str, Any], priority: float):
        """Store with priority score and decay clock"""
        self.conn.zadd("lightning:heap", {anchor_id: priority})
        self.conn.hset("lightning:data", anchor_id, json.dumps(data))
        self.conn.hset("lightning:meta", anchor_id, json.dumps({
            "created": time.time(),
            "last_accessed": time.time(),
            "access_count": 1
        }))
        
    def get(self, anchor_id: str) -> Optional[Dict]:
        """Sub-50ms access guaranteed by Redis"""
        data = self.conn.hget("lightning:data", anchor_id)
        if data:
            self.conn.hset("lightning:meta", anchor_id, json.dumps({
                "last_accessed": time.time(),
                "access_count": self.access_count(anchor_id) + 1
            }))
            return json.loads(data)
        return None
        
    def _run_decay(self):
        """Background decay process"""
        while self.running:
            self._apply_decay()
            time.sleep(self.decay_interval)
            
    def _apply_decay(self):
        """Redis-backed decay calculation"""
        for anchor_id in self.conn.zrange("lightning:heap", 0, -1):
            meta = json.loads(self.conn.hget("lightning:meta", anchor_id))
            age = time.time() - meta["created"]
            decayed_score = float(self.conn.zscore("lightning:heap", anchor_id)) * 0.95
            self.conn.zadd("lightning:heap", {anchor_id: decayed_score})
            
    def start(self):
        self.decay_thread.start()
        
    def stop(self):
        self.running = False
        self.decay_thread.join()