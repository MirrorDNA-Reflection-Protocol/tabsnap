"""Local filesystem storage for uploaded audio files."""

import os
import shutil
import uuid
from pathlib import Path

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data/outputs"))

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def ensure_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(filename: str, file_obj) -> tuple[str, str]:
    """Save uploaded file and return (job_id, file_path)."""
    ensure_dirs()
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported format: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    dest = job_dir / f"original{ext}"
    with open(dest, "wb") as out:
        shutil.copyfileobj(file_obj, out)

    return job_id, str(dest)


def job_output_dir(job_id: str) -> Path:
    """Return (and create) the output directory for a job."""
    d = OUTPUT_DIR / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d
