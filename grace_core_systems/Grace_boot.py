# grace_core_systems/central_intelligence/grace_boot.py

"""
Grace Boot Controller
Initializes core subsystems, validates trust state, and begins execution sequence.
"""

import time
import importlib
from datetime import datetime

# Core modules assumed to be present in the system
REQUIRED_MODULES = [
    'memory_controller',
    'memory_router',
    'ethics_bot',
    'unified_logic',
    'trust_orchestration',
    'validator',
    'interface_router',
    'auto_updater'
]

BOOT_STATE = {
    'version': '1.0.0',
    'timestamp': str(datetime.utcnow()),
    'verified_modules': [],
    'missing_modules': [],
    'boot_mode': 'sandbox',  # Options: sandbox, live, test
    'status': 'pending'
}

def verify_module(module_name):
    try:
        importlib.import_module(f'grace_core_systems.central_intelligence.{module_name}')
        return True
    except ImportError:
        return False

def bootstrap():
    print("\n[GRACE BOOT] Initiating boot sequence...\n")
    BOOT_STATE['status'] = 'initializing'

    for module in REQUIRED_MODULES:
        if verify_module(module):
            BOOT_STATE['verified_modules'].append(module)
            print(f"[BOOT] ✅ Verified module: {module}")
        else:
            BOOT_STATE['missing_modules'].append(module)
            print(f"[BOOT] ⚠️ Missing module: {module}")

    if not BOOT_STATE['missing_modules']:
        BOOT_STATE['status'] = 'healthy'
        print("\n[GRACE BOOT] All core systems verified. Entering mode:", BOOT_STATE['boot_mode'])
        launch_mode(BOOT_STATE['boot_mode'])
    else:
        BOOT_STATE['status'] = 'degraded'
        print("\n[GRACE BOOT] Boot completed in degraded mode. Triggering EvoCon fallback.")
        try:
            from grace_core_systems.central_intelligence import evo_controller
            evo_controller.initiate_recovery(BOOT_STATE)
        except ImportError:
            print("[EvoCon ERROR] evo_controller not found. Manual recovery required.")

    print("\n[GRACE BOOT] Status:", BOOT_STATE['status'])

def launch_mode(mode):
    if mode == 'sandbox':
        from grace_core_systems.central_intelligence import interface_router
        interface_router.start_sandbox()
    elif mode == 'live':
        from grace_core_systems.central_intelligence import interface_router
        interface_router.start_live()
    elif mode == 'test':
        from grace_core_systems.central_intelligence import interface_router
        interface_router.start_test()
    else:
        print("[BOOT] ❌ Unknown boot mode. Halting.")

if __name__ == "__main__":
    bootstrap()
