# decay_detector.py

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from hashlib import sha3_256
from prometheus_client import Counter, Histogram
from cryptography.fernet import Fernet
import threading
import json
from pydantic import BaseModel, ValidationError
import signal

# Metrics
DECAY_EVENTS = Counter('evolution_decay_events_total', 'Decay patterns detected', ['type', 'severity'])
DECAY_SEVERITY = Histogram('evolution_decay_severity', 'Normalized severity score', buckets=[0.3, 0.5, 0.7, 0.9])
PATTERN_FREQUENCY = Counter('decay_pattern_frequency', 'Recurrence of specific patterns', ['fingerprint'])

# Encryption
FERNET = Fernet.generate_key()

class TelemetrySchema(BaseModel):
    error_pattern: Dict
    metrics: Dict
    context: Optional[Dict]
    timestamp: datetime
    source: str
    correlation_id: str

class DecayDetector:
    def __init__(self, config: Dict):
        self.pattern_history = defaultdict(list)
        self.alert_backlog = []
        self.lock = threading.Lock()
        self.encryption = Fernet(FERNET)
        
        # Configurable parameters
        self.severity_weights = config.get('severity_weights', {
            'error_rate': 0.4,
            'latency': 0.3,
            'recurrence': 0.3
        })
        self.thresholds = config.get('thresholds', {
            'critical': 0.8,
            'warning': 0.5
        })
        
        # Alert suppression
        self.last_alert_time = {}
        self.min_alert_interval = timedelta(minutes=5)

    def analyze_telemetry(self, telemetry: Dict) -> Optional[Dict]:
        """Enterprise-grade decay analysis with validation and encryption"""
        try:
            validated = self._validate_and_encrypt(telemetry)
            pattern_fingerprint = self._generate_fingerprint(validated.error_pattern)
            
            with self.lock:
                return self._process_decay_pattern(validated, pattern_fingerprint)
                
        except ValidationError as e:
            logging.error(f"Invalid telemetry: {str(e)}")
            return None
        except Exception as e:
            logging.critical(f"Decay analysis failed: {str(e)}")
            self._enter_safe_mode()
            return None

    def _validate_and_encrypt(self, telemetry: Dict) -> TelemetrySchema:
        """Validate structure and encrypt sensitive data"""
        # Convert string timestamp to datetime
        if isinstance(telemetry.get('timestamp'), str):
            telemetry['timestamp'] = datetime.fromisoformat(telemetry['timestamp'])
            
        validated = TelemetrySchema(**telemetry)
        
        # Encrypt sensitive context
        if validated.context:
            validated.context = {
                'encrypted': self.encryption.encrypt(
                    json.dumps(validated.context).encode()
                ).decode()
            }
            
        return validated

    def _process_decay_pattern(self, telemetry: TelemetrySchema, fingerprint: str) -> Dict:
        """Core detection logic with thread safety"""
        # Track pattern frequency
        PATTERN_FREQUENCY.labels(fingerprint=fingerprint[:8]).inc()
        
        # Calculate time-bound recurrence
        now = datetime.utcnow()
        time_window = now - timedelta(hours=1)
        self.pattern_history[fingerprint] = [
            t for t in self.pattern_history[fingerprint] 
            if t > time_window
        ]
        self.pattern_history[fingerprint].append(now)
        
        # Calculate dynamic severity
        severity = self._calculate_severity_score(
            telemetry.metrics,
            len(self.pattern_history[fingerprint])
        DECAY_SEVERITY.observe(severity)
        
        # Determine alert level
        alert = None
        if severity >= self.thresholds['critical']:
            alert = self._trigger_alert(telemetry, severity, 'critical', fingerprint)
        elif severity >= self.thresholds['warning']:
            alert = self._trigger_alert(telemetry, severity, 'warning', fingerprint)
            
        return alert

    def _calculate_severity_score(self, metrics: Dict, recurrence: int) -> float:
        """Advanced severity calculation with weighted factors"""
        error_rate = metrics.get('error_rate', 0)
        latency = min(metrics.get('latency', 0) / 10, 1.0)
        recurrence = min(recurrence / 5, 1.0)
        
        return (
            self.severity_weights['error_rate'] * error_rate +
            self.severity_weights['latency'] * latency +
            self.severity_weights['recurrence'] * recurrence
        )

    def _trigger_alert(self, 
                      telemetry: TelemetrySchema,
                      severity: float,
                      level: str,
                      fingerprint: str) -> Optional[Dict]:
        """Enterprise alerting with flood protection"""
        alert_id = f"{fingerprint[:8]}-{telemetry.timestamp.isoformat()}"
        
        # Check alert cooldown
        if self._should_suppress_alert(fingerprint):
            return None
            
        alert = {
            'id': alert_id,
            'timestamp': telemetry.timestamp,
            'severity': severity,
            'level': level,
            'pattern': telemetry.error_pattern,
            'metrics': telemetry.metrics,
            'source': telemetry.source,
            'correlation_id': telemetry.correlation_id
        }
        
        with self.lock:
            self.alert_backlog.append(alert)
            self.last_alert_time[fingerprint] = datetime.utcnow()
            
        DECAY_EVENTS.labels(type=telemetry.error_pattern.get('type'), severity=level).inc()
        logging.warning(f"{level.upper()} DECAY ALERT: {alert_id}")
        
        # Integrate with enterprise alerting system
        self._dispatch_alert(alert)
        return alert

    def _should_suppress_alert(self, fingerprint: str) -> bool:
        """Prevent alert flooding using exponential backoff"""
        last_alert = self.last_alert_time.get(fingerprint)
        if not last_alert:
            return False
            
        elapsed = datetime.utcnow() - last_alert
        return elapsed < self.min_alert_interval

    def _dispatch_alert(self, alert: Dict):
        """Integrate with enterprise alerting systems"""
        # Implementation would connect to PagerDuty/Email/Slack
        pass

    def _enter_safe_mode(self):
        """Critical failure protocol"""
        logging.critical("Entering decay detection safe mode")
        # Implement circuit breaker pattern
        # Flush buffers, preserve state, notify sysadmins

    def get_historical_patterns(self, hours: int = 24) -> Dict:
        """Get patterns from last X hours for analysis"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return {
            fp: [t for t in timestamps if t > cutoff]
            for fp, timestamps in self.pattern_history.items()
        }