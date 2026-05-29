"""Song fingerprinting placeholder — Chromaprint/AcoustID (build order #15).

MVP: returns no match. Future: fingerprint with Chromaprint, look up via AcoustID.
"""

from __future__ import annotations


def fingerprint_audio(wav_path: str) -> dict | None:
    """Attempt to identify the song from its audio fingerprint.

    MVP: always returns None (no match).
    Future: return {"title": str, "artist": str, "external_id": str,
    "confidence": float, "provider": "acoustid"}.
    """
    return None
