# grace_core_systems/central_intelligence/bulk_whitelist_loader.py

"""
Bulk Whitelist Loader
Scans the whitelist archive directory and submits all files into the whitelist tracker queue.
Automatically logs hash, contributor, status, and ethics presence.
"""

import os
from pathlib import Path
from whitelist_queue_tracker import submit_to_whitelist

# Constants
ARCHIVE_DIR = Path("grace_core_systems/whitelist_archive/")
CONTRIBUTOR_ID = "legacy_archive"
DEFAULT_CATEGORY = "deepseek_refactor"

def load_whitelist_archive():
    if not ARCHIVE_DIR.exists():
        print(f"[Loader] ❌ Archive directory not found: {ARCHIVE_DIR}")
        return

    submitted = 0
    failed = 0

    for file in ARCHIVE_DIR.iterdir():
        if file.is_file() and file.suffix in [".py", ".txt", ".docx"]:
            result = submit_to_whitelist(
                file_path=str(file),
                contributor_id=CONTRIBUTOR_ID,
                category=DEFAULT_CATEGORY
            )
            if result:
                submitted += 1
            else:
                failed += 1

    print(f"\n[Loader] ✅ Submitted: {submitted} | ❌ Failed: {failed} | Total: {submitted + failed}")

if __name__ == "__main__":
    load_whitelist_archive()
