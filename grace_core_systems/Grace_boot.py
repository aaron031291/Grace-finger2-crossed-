# grace_core_systems/central_intelligence/grace_boot.py

"""
Grace Boot Sequencer
Routes input through pre-registry, registry, and verified system loaders.
"""

import time
import asyncio
import importlib
from datetime import datetime

from pre_registry.pre_registry_entry import GracePreRegistry, PreRegistryConfig
from grace_core_systems.registry.registry_system import RegistrySystem

BOOT_STATE = {
    'version': '2.0.0',
    'timestamp': str(datetime.utcnow()),
    'boot_mode': 'sandbox',  # Options: sandbox, live, test
    'verified_modules': [],
    'missing_modules': [],
    'pre_registry_passed': False,
    'registry_passed': False,
    'status': 'pending'
}

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

def verify_module(module_name):
    try:
        importlib.import_module(f'grace_core_systems.central_intelligence.{module_name}')
        return True
    except ImportError:
        return False

async def run_pre_registry():
    print("[BOOT] ➤ Running Pre-Registry Validation...")
    pre_registry = GracePreRegistry(PreRegistryConfig())
    report = await pre_registry.analyze_all_modules()
    passed = all([r.status.startswith("✅") for r in report.values()])
    BOOT_STATE['pre_registry_passed'] = passed
    print("[BOOT] Pre-Registry status:", "PASSED" if passed else "FAILED")
    return passed

def run_registry():
    print("[BOOT] ➤ Running Registry Indexing...")
    try:
        registry = RegistrySystem()
        result = registry.register_verified_modules()
        BOOT_STATE['registry_passed'] = result
        print("[BOOT] Registry status:", "PASSED" if result else "FAILED")
        return result
    except Exception as e:
        print(f"[BOOT ERROR] Registry execution failed: {str(e)}")
        return False

def verify_grace_core():
    print("[BOOT] ➤ Verifying Grace Core Modules...")
    for module in REQUIRED_MODULES:
        if verify_module(module):
            BOOT_STATE['verified_modules'].append(module)
            print(f"[BOOT] ✅ Verified: {module}")
        else:
            BOOT_STATE['missing_modules'].append(module)
            print(f"[BOOT] ⚠️ Missing: {module}")
    return len(BOOT_STATE['missing_modules']) == 0

def launch_mode(mode):
    from grace_core_systems.central_intelligence import interface_router
    if mode == 'sandbox':
        interface_router.start_sandbox()
    elif mode == 'live':
        interface_router.start_live()
    elif mode == 'test':
        interface_router.start_test()
    else:
        print("[BOOT] ❌ Unknown boot mode.")

async def bootstrap():
    print("\n[GRACE BOOT] Initializing verified boot sequence...\n")
    BOOT_STATE['status'] = 'initializing'

    pre_registry_ok = await run_pre_registry()
    if not pre_registry_ok:
        BOOT_STATE['status'] = 'halted_pre_registry'
        print("[BOOT] ❌ Halting. Pre-Registry failed.")
        return

    registry_ok = run_registry()
    if not registry_ok:
        BOOT_STATE['status'] = 'halted_registry'
        print("[BOOT] ❌ Halting. Registry failed.")
        return

    core_ok = verify_grace_core()
    if core_ok:
        BOOT_STATE['status'] = 'healthy'
        print("\n[GRACE BOOT] ✅ All systems verified. Launching:", BOOT_STATE['boot_mode'])
        launch_mode(BOOT_STATE['boot_mode'])
    else:
        BOOT_STATE['status'] = 'degraded'
        print("[GRACE BOOT] ⚠️ Grace will enter degraded mode. Invoking EvoCon fallback.")
        try:
            from grace_core_systems.central_intelligence import evo_controller
            evo_controller.initiate_recovery(BOOT_STATE)
        except ImportError:
            print("[EvoCon ERROR] ❌ Failed to load EvoCon recovery. Manual intervention required.")

    print("\n[GRACE BOOT] Final Status:", BOOT_STATE['status'])

# === Runtime Entry ===
if __name__ == "__main__":
    asyncio.run(bootstrap())
