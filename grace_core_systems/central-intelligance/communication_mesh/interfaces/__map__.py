# __map__.py — Internal Systems Loop Registry

INTERNAL_LOOP_MAP = {
    "trigger_router": {
        "entry": "signal_recorder.py",
        "score_engine": "absorption_score_engine.py",
        "ethics": "ethic_filter.py",
        "feedback": "feedback_log.py",
        "learning": "learning_loop.py",
        "decay": "decay_sandbox.py"
    },
    "entropy_monitoring": {
        "core": "entropy_feedback_tracker.py",
        "adjustment": "learning_loop.py"
    },
    "sandbox_reconciliation": {
        "loop": "loop_controller.py",
        "memory_bridge": "memory_hooks.py",
        "signal_router": "trigger_router.py"
    }
}