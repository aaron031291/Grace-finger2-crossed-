# auto_updater.py

import hashlib
import json
import logging
import difflib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from prometheus_client import Counter, Gauge, Histogram

# Metrics
LOGIC_UPDATES = Counter('logic_updates_total', 'Logic merge operations', ['source'])
LOGIC_CONFLICTS = Counter('logic_conflicts_total', 'Merge conflicts observed')
LOGIC_VARIANTS = Gauge('logic_active_variants', 'Parallel logic versions', ['function'])

@dataclass
class LogicBlock:
    content_hash: str
    code: str
    metadata: Dict
    lineage: List[str]
    active: bool = False

class LogicRegistry:
    def __init__(self):
        self.registry: Dict[str, LogicBlock] = {}  # hash -> block
        self.function_index: Dict[str, List[str]] = {}  # function -> [hashes]
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        self.public_key = self.private_key.public_key()
        
        # Trust configuration
        self.merge_policy = {
            "trust_weight": 0.6,
            "usage_weight": 0.3,
            "freshness_weight": 0.1
        }

    def merge_update(self, new_code: str, origin: Dict) -> str:
        """Sovereign merge entry point"""
        new_hash = self._content_hash(new_code)
        existing = self.registry.get(new_hash)
        
        if existing:
            LOGIC_UPDATES.labels(source='duplicate').inc()
            return new_hash

        # Identify function scope
        function_name = self._extract_function_name(new_code)
        if not function_name:
            raise InvalidLogicError("No clear function definition")

        # Generate metadata
        metadata = {
            "origin": origin,
            "fingerprint": self._sign_content(new_code),
            "last_updated": datetime.utcnow().isoformat(),
            "times_called": 0,
            "ethics_passed": [],
            "linked_anchors": [],
            "trust_score": self._calculate_trust(origin)
        }

        # Check for conflicts
        existing_hashes = self.function_index.get(function_name, [])
        conflict = self._detect_conflict(new_code, existing_hashes)

        if conflict:
            LOGIC_CONFLICTS.inc()
            resolved_hash = self._resolve_conflict(new_hash, new_code, metadata, existing_hashes)
        else:
            resolved_hash = self._register_new(new_hash, new_code, metadata, function_name)

        return resolved_hash

    def _detect_conflict(self, new_code: str, existing_hashes: List[str]) -> bool:
        """Check for semantic conflicts with existing logic"""
        if not existing_hashes:
            return False

        latest_existing = self.registry[existing_hashes[-1]].code
        diff = difflib.SequenceMatcher(None, latest_existing, new_code)
        return diff.ratio() < 0.95  # Threshold configurable

    def _resolve_conflict(self, new_hash: str, new_code: str, metadata: Dict, existing_hashes: List[str]) -> str:
        """Conflict resolution engine"""
        candidates = [new_hash] + existing_hashes
        scores = {}
        
        for candidate_hash in candidates:
            block = self.registry.get(candidate_hash, LogicBlock(
                content_hash=new_hash,
                code=new_code,
                metadata=metadata,
                lineage=[]
            ))
            scores[candidate_hash] = (
                block.metadata.get('trust_score', 0) * self.merge_policy["trust_weight"] +
                block.metadata.get('times_called', 0) * self.merge_policy["usage_weight"] +
                self._freshness_score(block) * self.merge_policy["freshness_weight"]
            )

        # Select highest scoring candidate
        winner = max(candidates, key=lambda h: scores[h])
        
        if winner != new_hash:
            LOGIC_UPDATES.labels(source='conflict_resolved').inc()
            return winner

        # Register new version but keep old active
        self._register_new(new_hash, new_code, metadata, self._extract_function_name(new_code))
        LOGIC_VARIANTS.labels(function=self._extract_function_name(new_code)).inc()
        
        # Run parallel validation
        self._parallel_execution(new_hash, existing_hashes[-1])
        
        return new_hash

    def _register_new(self, content_hash: str, code: str, metadata: Dict, function_name: str) -> str:
        """Add new logic to registry"""
        lineage = []
        if self.function_index.get(function_name):
            lineage = [self.function_index[function_name][-1]]
            
        block = LogicBlock(
            content_hash=content_hash,
            code=code,
            metadata=metadata,
            lineage=lineage
        )
        
        self.registry[content_hash] = block
        self.function_index.setdefault(function_name, []).append(content_hash)
        LOGIC_UPDATES.labels(source='new').inc()
        
        return content_hash

    def _parallel_execution(self, new_hash: str, old_hash: str):
        """Run competing logic versions in sandbox"""
        # Implementation would use sandbox_env
        # Monitor metrics to auto-promote better performing version
        pass

    def _calculate_trust(self, origin: Dict) -> float:
        """Calculate trust score based on origin"""
        # Factors: contributor reputation, validation passes, historical success
        return 0.8  # Simplified for example

    def _freshness_score(self, block: LogicBlock) -> float:
        """Calculate how recently updated the logic is"""
        days_old = (datetime.utcnow() - datetime.fromisoformat(block.metadata["last_updated"])).days
        return max(0, 1 - days_old/30)  # Linear decay over 30 days

    def _content_hash(self, code: str) -> str:
        """Generate content-addressable hash"""
        return hashlib.sha3_256(code.encode()).hexdigest()

    def _sign_content(self, code: str) -> str:
        """Cryptographically sign logic block"""
        return self.private_key.sign(
            code.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ).hex()

    def _extract_function_name(self, code: str) -> Optional[str]:
        """Simple function name extraction (would use AST parsing in production)"""
        lines = code.split('\n')
        for line in lines:
            if line.startswith('def '):
                return line.split(' ')[1].split('(')[0]
        return None

# Example Usage
if __name__ == "__main__":
    registry = LogicRegistry()
    
    # Initial version
    code_v1 = "def process_data(data):\n    return data.strip()"
    hash_v1 = registry.merge_update(code_v1, {"source": "whitelist", "contributor": "AI_TEAM_01"})
    
    # Conflicting update
    code_v2 = "def process_data(input):\n    return input.clean()"
    hash_v2 = registry.merge_update(code_v2, {"source": "contributor", "handle": "DEV_882"})
    
    print(f"Active variants: {LOGIC_VARIANTS.labels(function='process_data')._value.get()}")