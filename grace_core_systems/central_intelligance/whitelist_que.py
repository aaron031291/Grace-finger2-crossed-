# grace_core_systems/central_intelligence/whitelist_queue_tracker.py

"""
Whitelist Queue Tracker
Logs and audits submitted files, ideas, or modules for future evaluation and cognitive alignment.
Nothing is deleted—only archived, compressed, or deferred.
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("WhitelistQueue")
logger.setLevel(logging.INFO)

# Archive root
WHITELIST_DIR = Path("grace_core_systems/whitelist_archive/")
METADATA_LOG = WHITELIST_DIR / "submission_log.json"

# Ensure directory exists
WHITELIST_DIR.mkdir(parents=True, exist_ok=True)
if not METADATA_LOG.exists():
    METADATA_LOG.write_text(json.dumps([]))

# Submission structure
def submit_to_whitelist(file_path: str, contributor_id: str, category: str = "idea"):
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"[Whitelist] ❌ File not found: {file_path}")
        return False

    file_hash = hash_file(file_path)
    timestamp = str(datetime.utcnow())
    compressed_name = f"{file_hash[:10]}_{file_path.name}"
    archived_path = WHITELIST_DIR / compressed_name
    file_path.rename(archived_path)

    metadata = {
        "filename": file_path.name,
        "archived_name": compressed_name,
        "category": category,
        "hash": file_hash,
        "timestamp": timestamp,
        "contributor_id": contributor_id,
        "status": "queued",
        "ethics_header_found": scan_for_ethics_header(archived_path)
    }

    log_submission(metadata)
    logger.info(f"[Whitelist] ✅ Archived and logged: {file_path.name} as {compressed_name}")
    return True

def scan_for_ethics_header(path: Path) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return any("ethics" in line.lower() for line in lines[:10])
    except Exception:
        return False

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def log_submission(entry: dict):
    try:
        current_log = json.loads(METADATA_LOG.read_text())
        current_log.append(entry)
        METADATA_LOG.write_text(json.dumps(current_log, indent=2))
    except Exception as e:
        logger.error(f"[Whitelist] Failed to log submission: {e}")

def get_whitelist_log(filter_status: Optional[str] = None):
    try:
        log = json.loads(METADATA_LOG.read_text())
        if filter_status:
            return [entry for entry in log if entry["status"] == filter_status]
        return log
    except Exception as e:
        logger.error(f"[Whitelist] Log read error: {e}")
        return []

# Manual test
if __name__ == "__main__":
    test_path = "test_module_example.py"
    contributor = "anon_dev"
    category = "module_prototype"
    submit_to_whitelist(test_path, contributor, category)
    print(get_whitelist_log())
