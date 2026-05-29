"""Normalize uploaded audio to 16-bit WAV mono using FFmpeg."""

from __future__ import annotations

import subprocess
from pathlib import Path


def normalize_audio(input_path: str, output_dir: Path) -> str:
    """Convert any supported audio to 44.1kHz 16-bit mono WAV.

    Returns path to the normalized WAV file.
    """
    out_path = output_dir / "normalized.wav"
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "44100",
        "-ac", "1",
        "-sample_fmt", "s16",
        "-t", "30",  # MVP: cap at 30 seconds
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg normalization failed: {result.stderr[:500]}")
    if not out_path.exists():
        raise FileNotFoundError(f"Normalized file not created: {out_path}")
    return str(out_path)
