##############################################
# ethical_constraints.py
##############################################

ETHICAL_RULES = {
    "no_harm": lambda p: p['cost'] < 0.8,
    "transparency": lambda p: "blackbox" not in p['logic']
}

class EthicalValidator:
    @staticmethod
    def check_ethics(proposal: Dict) -> bool:
        return all(
            rule(proposal) 
            for rule in ETHICAL_RULES.values()
        )

    @staticmethod
    def flag_violation(agent_id: str, reason: str):
        TrustReflector.reflect_trust_feedback(agent_id, "violation")
        NegotiationState.log_event(
            agent_id,
            f"Ethical violation: {reason}"
        )