from pathlib import Path
import hashlib
import json
import traceback

# Define the path where incoming modules or files would be simulated
INCOMING_PATH = Path("incoming_modules")
LOG_PATH = Path("pre_registry_logs")
LOG_PATH.mkdir(exist_ok=True)
INCOMING_PATH.mkdir(exist_ok=True)

def validate_module_syntax(file_path):
    try:
        with open(file_path, "r") as f:
            compile(f.read(), file_path.name, "exec")
        return True, None
    except Exception as e:
        return False, str(e)

def generate_cryptographic_id(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
        return hashlib.sha256(file_data).hexdigest()

def pre_register_modules():
    report = {}
    for file in INCOMING_PATH.glob("*.py"):
        module_id = generate_cryptographic_id(file)
        valid, error = validate_module_syntax(file)
        if valid:
            report[file.name] = {
                "Status": "✅ Passed Syntax Check",
                "ModuleID": module_id
            }
        else:
            report[file.name] = {
                "Status": "❌ Failed Syntax Check",
                "Error": error
            }
    with open(LOG_PATH / "pre_registry_report.json", "w") as log_file:
        json.dump(report, log_file, indent=4)
    return report

pre_register_modules()
