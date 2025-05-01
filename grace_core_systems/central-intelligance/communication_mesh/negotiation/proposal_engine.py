##############################################
# proposal_engine.py
##############################################

from pydantic import BaseModel, ValidationError
from typing import Dict, Any

class ProposalSchema(BaseModel):
    goal: str
    logic: Dict[str, Any]
    cost: float
    fallback: Dict[str, Any]
    context: Dict[str, float]

class ProposalEngine:
    @staticmethod
    def generate_proposal(agent_id: str, context: Dict) -> Dict:
        return {
            "goal": context.get("goal"),
            "logic": context.get("logic"),
            "cost": context.get("cost", 0.0),
            "fallback": context.get("fallback"),
            "context": {
                "urgency": context.get("urgency", 0.5),
                "confidence": context.get("confidence", 0.7)
            },
            "agent_id": agent_id
        }

    @staticmethod
    def validate_proposal_schema(proposal: Dict) -> bool:
        try:
            ProposalSchema(**proposal)
            return True
        except ValidationError:
            return False 