"""
Lightning Bus – Grace's unified signal router and cryptographic event verifier.
Extends the HyperCommBus and Rationale Ledger into a modular pub-sub + fingerprint layer.
"""

import hashlib
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Internal signal vault for transient messaging
LIGHTNING_VAULT = []

# Default decay in seconds
DEFAULT_TTL = 30

class LightningSignal:
    def __init__(self, signal_type: str, payload: Dict, ttl: int = DEFAULT_TTL):
        self.signal_type = signal_type
        self.payload = payload
        self.timestamp = datetime.utcnow()
        self.expiry = self.timestamp + timedelta(seconds=ttl)
        self.fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self) -> str:
        unique_str = f"{self.signal_type}|{self.timestamp.isoformat()}|{uuid.uuid4()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expiry

    def to_dict(self) -> Dict:
        return {
            "type": self.signal_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "fingerprint": self.fingerprint,
            "expires": self.expiry.isoformat()
        }

class LightningBus:
    def __init__(self):
        self.subscribers: Dict[str, List[str]] = {}

    def publish(self, signal_type: str, payload: Dict, ttl: int = DEFAULT_TTL) -> Dict:
        signal = LightningSignal(signal_type, payload, ttl)
        LIGHTNING_VAULT.append(signal)
        return signal.to_dict()

    def subscribe(self, module_name: str, signal_type: str):
        if module_name not in self.subscribers:
            self.subscribers[module_name] = []
        self.subscribers[module_name].append(signal_type)

    def fetch_signals(self, module_name: str) -> List[Dict]:
        if module_name not in self.subscribers:
            return []

        subscribed_types = self.subscribers[module_name]
        active_signals = []

        for signal in LIGHTNING_VAULT:
            if not signal.is_expired() and signal.signal_type in subscribed_types:
                active_signals.append(signal.to_dict())

        return active_signals

    def decay_expired(self):
        global LIGHTNING_VAULT
        LIGHTNING_VAULT = [s for s in LIGHTNING_VAULT if not s.is_expired()]

    def validate_fingerprint(self, fingerprint: str) -> bool:
        return any(s.fingerprint == fingerprint for s in LIGHTNING_VAULT if not s.is_expired())

# Grace system-level instance
lightning = LightningBus()
