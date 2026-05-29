"""Stem separation placeholder — Demucs integration (build order #14).

For MVP, this is a pass-through. When Demucs is added, this module
will separate the audio into stems and return the guitar-candidate stem.
"""

from __future__ import annotations

from pathlib import Path


def separate_stems(wav_path: str, output_dir: Path) -> dict[str, str]:
    """Separate audio into stems.

    MVP: returns the original WAV as the 'other' stem.
    Future: run Demucs and return {"vocals": path, "drums": path,
    "bass": path, "other": path}.
    """
    return {"other": wav_path}
