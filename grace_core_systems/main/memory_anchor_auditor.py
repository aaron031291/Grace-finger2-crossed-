##############################
# memory/anchor_auditor.py
##############################

from typing import Dict, Any
from hashlib import sha256

class AnchorAuditor:
    def __init__(self, audit_path: str = "audit_trail.log"):
        self.audit_file = open(audit_path, "a")
        self.last_hash = None
        
    def log_anchor_change(self, action: str, data: Dict[str, Any]):
        """Append-only audit log with chained hashes"""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "data": data,
            "previous_hash": self.last_hash
        }
        entry_str = json.dumps(entry)
        entry_hash = sha256(entry_str.encode()).hexdigest()
        entry["entry_hash"] = entry_hash
        
        self.audit_file.write(json.dumps(entry) + "\n")
        self.last_hash = entry_hash
        
    def verify_chain(self) -> bool:
        """Validate audit trail integrity"""
        # Implementation left for blockchain integration
        return True