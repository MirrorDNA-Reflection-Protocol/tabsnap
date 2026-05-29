"""Confidence scoring for transcription results."""

from __future__ import annotations


def score_confidence(
    notes: list[dict],
    ambiguity: float,
    tempo_bpm: float,
) -> dict:
    """Compute per-dimension and overall confidence scores.

    Returns {"overall": float, "pitch": float, "rhythm": float,
             "fretboard": float, "technique": float}.
    """
    if not notes:
        return {"overall": 0.0, "pitch": 0.0, "rhythm": 0.0, "fretboard": 0.0, "technique": 0.0}

    # --- Pitch confidence ---
    # Average Basic Pitch confidence across notes
    pitch_confs = [n.get("confidence", 0.5) for n in notes]
    pitch = sum(pitch_confs) / len(pitch_confs)

    # --- Rhythm confidence ---
    # Penalize extreme tempos (probably detection error)
    rhythm = 0.8
    if tempo_bpm < 50 or tempo_bpm > 220:
        rhythm *= 0.6
    # Penalize very short note density (polyphony / noise)
    note_density = len(notes) / max(1.0, max(n["end"] for n in notes) - min(n["start"] for n in notes))
    if note_density > 20:  # More than 20 notes/sec is suspicious
        rhythm *= 0.5
    elif note_density > 10:
        rhythm *= 0.7

    # --- Fretboard confidence ---
    # Lower ambiguity = more certain assignment
    # ambiguity ~1.0 means only one option per note (high confidence)
    # ambiguity ~3.0+ means many options (lower confidence)
    fretboard = max(0.1, min(1.0, 1.5 / max(ambiguity, 0.5)))

    # --- Technique confidence ---
    # MVP: always low since we don't detect bends, slides, hammer-ons
    technique = 0.25

    # --- Overall ---
    overall = (pitch * 0.35 + rhythm * 0.25 + fretboard * 0.30 + technique * 0.10)

    return {
        "overall": round(overall, 2),
        "pitch": round(pitch, 2),
        "rhythm": round(rhythm, 2),
        "fretboard": round(fretboard, 2),
        "technique": round(technique, 2),
    }


def confidence_label(overall: float) -> str:
    """Human-readable confidence label."""
    if overall >= 0.80:
        return "Strong draft"
    if overall >= 0.60:
        return "Playable draft"
    if overall >= 0.40:
        return "Needs review"
    return "Experimental"
