from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from cryptography.fernet import Fernet
from datetime import datetime
import hashlib
import logging

class ComplianceStandard(Enum):
    GDPR = "gdpr"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    HIPAA = "hipaa"

class ComplianceViolation(Exception):
    pass

class ComplianceEngine:
    def __init__(self, encryption_key: str):
        self.encryption = Fernet(encryption_key)
        self.standards_status: Dict[ComplianceStandard, bool] = {
            standard: False for standard in ComplianceStandard
        }
        self.violation_log: List[Dict] = []
        self.audit_trail: List[Dict] = []

    def validate(self, operation: Dict, required: List[ComplianceStandard]) -> bool:
        """Primary firewall for runtime compliance enforcement."""
        all_passed = True
        for standard in required:
            validator = getattr(self, f"_validate_{standard.value}", None)
            if not validator:
                raise ValueError(f"No validator defined for {standard.value}")
            
            passed, reason = validator(operation)
            if not passed:
                all_passed = False
                self._log_violation(operation, standard, reason)
        
        return all_passed

    def _validate_gdpr(self, op: Dict) -> Tuple[bool, str]:
        if "data_subject" in op and not op.get("consent_mechanism"):
            return False, "Missing consent mechanism"
        if "data_transfer" in op and "EU" in op.get("regions", []):
            return False, "Unauthorized EU data transfer"
        return True, ""

    def _validate_iso_27001(self, op: Dict) -> Tuple[bool, str]:
        if op.get("encryption_strength", 0) < 256:
            return False, "Insufficient encryption"
        if not op.get("access_controls"):
            return False, "Missing access control"
        return True, ""

    def _validate_soc2(self, op: Dict) -> Tuple[bool, str]:
        if not op.get("audit_logging"):
            return False, "SOC2: Audit logging disabled"
        return True, ""

    def _validate_hipaa(self, op: Dict) -> Tuple[bool, str]:
        if "PHI" in op.get("data_type", "") and not op.get("data_masking"):
            return False, "HIPAA: PHI without masking"
        return True, ""

    def _log_violation(self, op: Dict, standard: ComplianceStandard, reason: str):
        encrypted = self.encryption.encrypt(json.dumps(op).encode())
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "standard": standard.value,
            "operation_hash": hashlib.sha256(encrypted).hexdigest(),
            "reason": reason
        }
        self.violation_log.append(entry)
        logging.warning(f"[Compliance Violation] {standard.value}: {reason}")
        self._escalate_to_parliament(entry)

    def _escalate_to_parliament(self, entry: Dict):
        # Trigger system-level review if needed
        logging.critical(f"[Parliament Alert] Compliance violation escalated: {entry['reason']}")

    def generate_report(self, standard: ComplianceStandard, format: str = "json") -> str:
        filtered = [v for v in self.violation_log if v["standard"] == standard.value]
        report = {
            "standard": standard.value,
            "status": self.standards_status.get(standard, False),
            "violations": filtered,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(report, indent=2)

class ComplianceMonitor:
    """State observer for compliance alignment"""
    def __init__(self, engine: ComplianceEngine):
        self.engine = engine
        self.snapshot = {}

    def check_all(self) -> Dict:
        now = datetime.utcnow().isoformat()
        self.snapshot = {
            standard.value: {
                "compliant": self.engine.standards_status[standard],
                "last_checked": now
            }
            for standard in ComplianceStandard
        }
        return self.snapshot
    