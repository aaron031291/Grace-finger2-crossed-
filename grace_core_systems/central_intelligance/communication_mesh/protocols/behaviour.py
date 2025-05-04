import time
import logging
from enum import Enum
from typing import Dict, Callable
from dataclasses import dataclass
from prometheus_client import Counter, Gauge, Histogram
from circuitbreaker import circuit
import psutil
import threading
from functools import lru_cache

# --- Metrics ---
POLICY_CHANGES = Counter('behavior_policy_changes', 'Policy change events')
POLICY_APPLICATIONS = Counter('behavior_policy_applications', 'Policy executions', ['policy'])
ADAPTIVE_FACTOR = Gauge('adaptive_load_factor', 'Composite load factor')
DECISION_LATENCY = Histogram('behavior_decision_latency', 'Policy application time')

# --- Configuration ---
@dataclass
class BehaviorConfig:
    adaptive_window: int = 60
    aggressive_cpu_threshold: float = 0.2
    conservative_cpu_threshold: float = 0.8
    min_adaptive_interval: float = 2.0

class BehaviorPolicy(Enum):
    DEFAULT = "default"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"

# --- Metrics Collector ---
class SystemMetricsCollector:
    def __init__(self):
        self._load_history = []
        self._lock = threading.Lock()

    @lru_cache(maxsize=1)
    def get_load_factor(self) -> float:
        cpu = psutil.cpu_percent() / 100
        mem = psutil.virtual_memory().percent / 100
        queue = 0.1  # Placeholder
        return 0.6 * cpu + 0.3 * mem + 0.1 * queue

    def update_load_history(self):
        now = time.time()
        with self._lock:
            self._load_history = [
                (ts, factor) for ts, factor in self._load_history
                if ts > now - BehaviorHandler.config.adaptive_window
            ]
            self._load_history.append((now, self.get_load_factor()))

# --- Behavior Handler ---
class BehaviorHandler:
    config = BehaviorConfig()

    def __init__(self, config: BehaviorConfig = BehaviorConfig()):
        self.config = config
        BehaviorHandler.config = config
        self.policy = BehaviorPolicy.DEFAULT
        self.metrics = SystemMetricsCollector()
        self._policy_lock = threading.Lock()
        self._last_adaptive = 0.0
        self.policy_map = {
            BehaviorPolicy.DEFAULT: self._default_behavior,
            BehaviorPolicy.AGGRESSIVE: self._aggressive_behavior,
            BehaviorPolicy.CONSERVATIVE: self._conservative_behavior,
            BehaviorPolicy.ADAPTIVE: self._adaptive_behavior
        }

    @DECISION_LATENCY.time()
    def apply(self, message: Dict) -> Dict:
        try:
            with self._policy_lock:
                handler = self.policy_map.get(self.policy, self._default_behavior)
            POLICY_APPLICATIONS.labels(policy=self.policy.value).inc()
            return handler(message)
        except Exception as e:
            logging.error("Behavior policy failed, using failsafe", exc_info=e)
            return self._failsafe_behavior(message)

    @circuit(failure_threshold=3, recovery_timeout=30)
    def set_policy(self, policy: BehaviorPolicy):
        with self._policy_lock:
            if self.policy != policy:
                self.policy = policy
                POLICY_CHANGES.inc()
                logging.info(f"Behavior policy changed to {policy.name}")

    def register_policy(self, name: str, handler: Callable):
        with self._policy_lock:
            self.policy_map[name] = handler

    # --- Default Policies ---
    def _default_behavior(self, message: Dict) -> Dict:
        return {**message, "priority": 3, "timeout": 3.0, "retry_limit": 3, "bandwidth_limit": "auto"}

    def _aggressive_behavior(self, message: Dict) -> Dict:
        return {**message, "priority": 1, "timeout": 1.0, "retry_limit": 5, "bandwidth_limit": "unlimited"}

    def _conservative_behavior(self, message: Dict) -> Dict:
        return {**message, "priority": 5, "timeout": 5.0, "retry_limit": 1, "bandwidth_limit": "low"}

    def _adaptive_behavior(self, message: Dict) -> Dict:
        now = time.time()
        if now - self._last_adaptive > self.config.min_adaptive_interval:
            self.metrics.update_load_history()
            self._last_adaptive = now
        load_factor = self.metrics.get_load_factor()
        ADAPTIVE_FACTOR.set(load_factor)

        if load_factor > self.config.conservative_cpu_threshold:
            return self._conservative_behavior(message)
        elif load_factor < self.config.aggressive_cpu_threshold:
            return self._aggressive_behavior(message)
        else:
            return self._default_behavior(message)

    def _failsafe_behavior(self, message: Dict) -> Dict:
        return {**message, "priority": 4, "timeout": 10.0, "retry_limit": 0, "bandwidth_limit": "strict"}

# --- Custom Registration Example ---
def custom_behavior(message: Dict) -> Dict:
    if message.get("emergency"):
        return {**message, "priority": 0}
    return message

# --- Runtime Usage Example ---
if __name__ == "__main__":
    handler = BehaviorHandler()
    handler.set_policy(BehaviorPolicy.ADAPTIVE)
    handler.register_policy("emergency", custom_behavior)

    message_context = {
        "payload": {"task": "hotfix"},
        "route": "ai_core",
        "qos": "guaranteed",
        "emergency": True
    }

    processed = handler.apply(message_context)
    print("Processed Message:", processed)

"""
Adaptive Decision Matrix — Runtime Behavior Coordination

```mermaid
graph TD
    A[Adaptive Policy] --> B[Load Factor]
    B -->|Low| C[Aggressive]
    B -->|High| D[Conservative]
    B -->|Medium| E[Default]
    C --> F[Max Retries=5]
    D --> G[Max Retries=1]
    E --> H[Max Retries=3] 
    """