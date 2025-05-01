from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, validator, Field
from datetime import datetime, timedelta
import os, json, hashlib, logging, jwt
from prometheus_client import Counter, Gauge
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# --- Metrics ---
PHILOSOPHY_CHANGES = Counter('core_philosophy_changes', 'Changes to philosophical core')
DECISION_REJECTIONS = Counter('core_rejected_actions', 'Actions rejected by philosophy core', ['reason'])
CONTRACT_GAUGE = Gauge('core_contract_alignment', 'Alignment with relational contracts', ['contract_type'])
OVERRIDE_ATTEMPTS = Counter('philosophy_override_attempts', 'Override attempts', ['type', 'success'])
DOCTRINE_AGE = Gauge('philosophy_doctrine_age', 'Current doctrine version age in seconds')

# --- Config Model ---
class PhilosophyConfig(BaseModel):
    foundational_values: List[str] = Field(..., min_items=5)
    system_directives: List[str]
    relational_contracts: Dict[str, str]
    decision_filters: Dict[str, any]
    version: str = "1.0.0"
    effective_date: datetime
    cryptographic_hash: Optional[str]
    previous_version_hash: Optional[str]

    @validator('foundational_values')
    def validate_core_values(cls, v):
        required = {"Honesty", "Integrity", "Accountability"}
        if not required.issubset(set(v)):
            raise ValueError("Core values must include Honesty, Integrity, and Accountability")
        return v

# --- Sovereign Signature Validator ---
class OverrideGuard:
    def __init__(self, required_signers: int = 3):
        self.required_signers = required_signers
        self.override_log = []
        self.authorized_parties = {
            "founder": self._load_public_key("FOUNDER_PUB_KEY"),
            "ethics_board": self._load_public_key("ETHICS_PUB_KEY"),
            "system_guardian": self._load_public_key("GUARDIAN_PUB_KEY")
        }

    def _load_public_key(self, env_var: str):
        key_data = os.getenv(env_var, "")
        return serialization.load_pem_public_key(key_data.encode())

    def validate_override(self, operation: str, signatures: Dict[str, str]) -> bool:
        op_hash = hashlib.sha3_256(operation.encode()).digest()
        valid = 0

        for party, sig in signatures.items():
            pk = self.authorized_parties.get(party)
            if not pk:
                continue
            try:
                pk.verify(
                    bytes.fromhex(sig),
                    op_hash,
                    padding.PSS(mgf=padding.MGF1(hashes.SHA3_256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA3_256()
                )
                valid += 1
            except Exception as e:
                logging.warning(f"Invalid signature from {party}: {e}")

        if valid >= self.required_signers:
            self.override_log.append({"timestamp": datetime.utcnow(), "operation": operation, "signers": list(signatures)})
            OVERRIDE_ATTEMPTS.labels(type="doctrine_override", success=True).inc()
            return True

        OVERRIDE_ATTEMPTS.labels(type="doctrine_override", success=False).inc()
        return False

# --- Core Philosophy Logic ---
class PhilosophyCore:
    def __init__(self, config_path: str, encryption_key: Optional[str] = None):
        self.fernet = Fernet(encryption_key) if encryption_key else None
        self._current_doctrine = None
        self._version_history = []
        self.override_guard = OverrideGuard()
        self.load_doctrine(config_path)

    def load_doctrine(self, path_or_data, migration_signatures: Optional[Dict[str, str]] = None) -> bool:
        try:
            if isinstance(path_or_data, str):  # File path
                with open(path_or_data, 'r') as f:
                    raw = f.read()
                    if self.fernet:
                        raw = self.fernet.decrypt(raw.encode()).decode()
                    data = json.loads(raw)
            else:
                data = path_or_data  # Assume it's a dict

            doctrine = PhilosophyConfig(**data)
            self._validate_integrity(doctrine)

            if migration_signatures:
                op_desc = f"DoctrineUpdate-{datetime.utcnow().isoformat()}"
                if not self.override_guard.validate_override(op_desc, migration_signatures):
                    raise PermissionError("Multi-party override rejected")

            if self._current_doctrine:
                self._version_history.append(self._current_doctrine)

            self._current_doctrine = doctrine
            PHILOSOPHY_CHANGES.inc()
            DOCTRINE_AGE.set((datetime.utcnow() - doctrine.effective_date).total_seconds())
            for contract in doctrine.relational_contracts:
                CONTRACT_GAUGE.labels(contract_type=contract).set(1.0)

            return True

        except Exception as e:
            logging.error(f"Doctrine load failed: {e}")
            return False

    def _validate_integrity(self, doctrine: PhilosophyConfig):
        doctrine_json = doctrine.json(exclude={'cryptographic_hash'})
        digest = hashlib.sha3_256(doctrine_json.encode()).hexdigest()
        if doctrine.cryptographic_hash and doctrine.cryptographic_hash != digest:
            raise ValueError("Philosophy core tampering detected")
        if self._version_history and \
           doctrine.previous_version_hash != self._version_history[-1].cryptographic_hash:
            raise ValueError("Version mismatch in doctrine history")

    def should_reject_action(self, alignment_score: float, conflicted: bool, founder_sync: bool, override_token: Optional[str] = None) -> Tuple[bool, List[str]]:
        reasons = []
        f = self._current_doctrine.decision_filters

        if f.get("reject_if_conflicted") and conflicted:
            DECISION_REJECTIONS.labels(reason="conflict").inc()
            reasons.append("conflict")

        if f.get("force_review_if_founder_out_of_sync") and not founder_sync:
            DECISION_REJECTIONS.labels(reason="founder_sync").inc()
            reasons.append("founder_sync")

        if f.get("alignment_required") and alignment_score < f.get("value_floor", 0.75):
            DECISION_REJECTIONS.labels(reason="alignment").inc()
            reasons.append("alignment")

        if reasons and override_token:
            try:
                payload = jwt.decode(override_token, os.getenv("SOVEREIGN_JWT_SECRET"), algorithms=["HS256"])
                if payload.get("aud") == "philosophy_override":
                    return False, ["override_active"]
            except jwt.PyJWTError as e:
                logging.error(f"JWT override token invalid: {e}")

        return bool(reasons), reasons

    def audit_contract_compliance(self, entity: str, action: Dict) -> float:
        score = 0.85  # Placeholder: real NLP scoring could go here
        CONTRACT_GAUGE.labels(contract_type=entity).set(score)
        return score

    def generate_manifest_report(self) -> Dict:
        doc = self._current_doctrine
        return {
            "version": doc.version,
            "effective_date": doc.effective_date.isoformat(),
            "value_coverage": self._value_coverage(),
            "contract_alignment": {
                e: self.audit_contract_compliance(e, {}) for e in doc.relational_contracts
            }
        }

    def _value_coverage(self) -> Dict:
        return {v: 0.95 for v in self._current_doctrine.foundational_values}