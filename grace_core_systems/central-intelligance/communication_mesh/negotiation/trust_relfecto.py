##############################################
# trust_reflector.py
##############################################

from typing import Dict
from collections import defaultdict

class TrustRegistry:
    _instance = None
    trust_scores = defaultdict(lambda: 0.7)
    performance_log = defaultdict(list)

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

class TrustReflector:
    @staticmethod
    def compute_trust(agent_id: str, context: Dict) -> float:
        registry = TrustRegistry()
        base_score = registry.trust_scores[agent_id]
        # Contextual modifiers
        if context.get('critical_priority'):
            return min(base_score * 1.2, 1.0)
        return base_score

    @staticmethod
    def reflect_trust_feedback(agent_id: str, outcome: str):
        registry = TrustRegistry()
        adjustment = 0.1 if outcome == "success" else -0.15
        registry.trust_scores[agent_id] = max(0.1, min(1.0, 
            registry.trust_scores[agent_id] + adjustment
        ))