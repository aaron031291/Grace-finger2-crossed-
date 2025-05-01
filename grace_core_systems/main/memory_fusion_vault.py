##############################
# memory/fusion_vault.py
##############################

import sqlite3
import json
from hashlib import sha256
from typing import Dict, Any, List
from pydantic import BaseModel

class FusionConfig(BaseModel):
    db_path: str = "fusion_vault.db"
    immutable_mode: bool = True

class FusionVault:
    def __init__(self, config: FusionConfig):
        self.conn = sqlite3.connect(config.db_path)
        self._init_db()
        self.immutable = config.immutable_mode
        
    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS anchors (
                    id TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    versions TEXT NOT NULL,
                    merkle_proof TEXT NOT NULL,
                    created REAL NOT NULL,
                    modified REAL NOT NULL
                )
            """)
            
    def anchor(self, data: Dict[str, Any], previous_hash: str = None) -> str:
        """Store immutable data with versioning"""
        content_hash = self._hash_data(data)
        versions = json.dumps([content_hash])
        merkle_proof = self._build_merkle_proof(content_hash, previous_hash)
        
        with self.conn:
            self.conn.execute("""
                INSERT INTO anchors (id, content_hash, versions, merkle_proof, created, modified)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['id'], content_hash, versions, merkle_proof, 
                  data['timestamp'], data['timestamp']))
            
        return content_hash
    
    def _hash_data(self, data: Dict) -> str:
        return sha256(json.dumps(data).encode()).hexdigest()
        
    def _build_merkle_proof(self, current_hash: str, previous_hash: str) -> str:
        return sha256(f"{previous_hash}|{current_hash}".encode()).hexdigest()