# # io_layer/zip_utils.py
# # Utility functions for handling ZIP files, including validation, extraction, and checksum calculation.

import hashlib
import os
import shutil
import zipfile
from pathlib import Path

## ZIP Handling Utilities
def is_zip_file(path: str | Path) -> bool:
    """Return True if the given path is a valid ZIP file."""
    path = Path(path)
    return path.is_file() and zipfile.is_zipfile(path)


def zip_checksum(zip_path: str | Path) -> str:
    """Return an MD5 hash of the zip file contents."""
    zip_path = Path(zip_path)
    h = hashlib.md5()
    with open(zip_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_zip(zip_path: str | Path, target_dir: str | Path) -> Path:
    """
    Extract a ZIP file into target_dir, but only if the zip has changed
    since the last extraction (checked via MD5 checksum).

    - On first run: extracts and saves a .checksum sentinel file.
    - On subsequent runs: compares checksums; skips if unchanged.
    - If the zip changed: wipes target_dir and re-extracts cleanly.

    Returns the path to the extracted folder.
    """
    zip_path   = Path(zip_path)
    target_dir = Path(target_dir)

    if not is_zip_file(zip_path):
        raise ValueError(f"Not a valid zip file: {zip_path}")

    current_checksum  = zip_checksum(zip_path)
    checksum_file     = target_dir / ".checksum"

    # Check if we can skip extraction
    if target_dir.exists() and checksum_file.exists():
        stored = checksum_file.read_text().strip()
        if stored == current_checksum:
            return target_dir  # zip unchanged — reuse existing files

    # Zip changed (or first run) — wipe and re-extract cleanly
    if target_dir.exists():
        import stat
        def _handle_readonly(func, path, exc):
            # On Windows, files can be read-only or locked — force permissions and retry
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass  # if still locked, ignore and overwrite on extraction
        shutil.rmtree(target_dir, onerror=_handle_readonly)

    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(target_dir)

    # Save checksum so next run can skip if unchanged
    checksum_file.write_text(current_checksum)

    return target_dir # return the path to the extracted folder for downstream use