"""Snap MIDI note timings to the nearest beat grid."""

from __future__ import annotations

from .fretboard import MidiNote


def quantize_notes(
    notes: list[MidiNote],
    tempo_bpm: float,
    subdivision: int = 4,
) -> list[MidiNote]:
    """Quantize note start/end times to the nearest grid position.

    subdivision=4 means 16th notes (4 per beat).
    """
    if not notes or tempo_bpm <= 0:
        return notes

    beat_duration = 60.0 / tempo_bpm
    grid_size = beat_duration / subdivision

    quantized = []
    for n in notes:
        q_start = round(n.start / grid_size) * grid_size
        q_end = round(n.end / grid_size) * grid_size
        # Ensure minimum note duration of one grid unit
        if q_end <= q_start:
            q_end = q_start + grid_size
        quantized.append(MidiNote(
            pitch=n.pitch,
            start=round(q_start, 6),
            end=round(q_end, 6),
            velocity=n.velocity,
        ))
    return quantized
