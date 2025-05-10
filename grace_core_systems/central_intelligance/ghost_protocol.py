# grace_core_systems/central_intelligence/ghost_protocol_access.py

"""
Ghost Protocol Access
Cryptographic shape-based access system for Grace's unified interface.
Eliminates traditional username/passwords using pattern + vector + entropy verification.
"""

import hashlib
import time
import logging
from typing import Dict

logger = logging.getLogger("GhostAccess")
logger.setLevel(logging.INFO)

# Shape-based identity store (in-memory for now; can move to DB)
SHAPE_REGISTRY: Dict[str, Dict] = {}

def hash_shape_vector(shape_pattern: str, entropy_key: str) -> str:
    composite = f"{shape_pattern}:{entropy_key}"
    return hashlib.sha256(composite.encode()).hexdigest()

def register_identity(identity_id: str, shape_pattern: str, entropy_key: str, role: str = "contributor"):
    shape_hash = hash_shape_vector(shape_pattern, entropy_key)
    timestamp = time.time()

    SHAPE_REGISTRY[identity_id] = {
        "shape_hash": shape_hash,
        "timestamp": timestamp,
        "role": role,
        "active": True
    }

    logger.info(f"[Ghost] ✅ Registered {identity_id} with role: {role}")
    return shape_hash

def validate_access(identity_id: str, shape_pattern: str, entropy_key: str) -> bool:
    if identity_id not in SHAPE_REGISTRY:
        logger.warning(f"[Ghost] ⚠️ Unknown identity: {identity_id}")
        return False

    submitted_hash = hash_shape_vector(shape_pattern, entropy_key)
    stored_hash = SHAPE_REGISTRY[identity_id]["shape_hash"]

    if submitted_hash == stored_hash:
        logger.info(f"[Ghost] ✅ Access granted for: {identity_id}")
        return True
    else:
        logger.warning(f"[Ghost] ❌ Access denied for: {identity_id}")
        return False

def revoke_identity(identity_id: str):
    if identity_id in SHAPE_REGISTRY:
        SHAPE_REGISTRY[identity_id]["active"] = False
        logger.info(f"[Ghost] 🔒 Identity revoked: {identity_id}")
        return True
    return False

def list_active_identities():
    return {k: v for k, v in SHAPE_REGISTRY.items() if v["active"]}

# Example test
if __name__ == "__main__":
    register_identity("alpha_user", "hex-spiral-grid", "X9Y7Z3", "admin")
    assert validate_access("alpha_user", "hex-spiral-grid", "X9Y7Z3")
    assert not validate_access("alpha_user", "hex-spiral-grid", "WRONGKEY")
    print(list_active_identities())
