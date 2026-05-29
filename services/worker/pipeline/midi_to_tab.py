"""Bridge between MIDI note dicts and tab-core fretboard solver."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure tab-core is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "packages"))

from tab_core import MidiNote, FretPosition, solve_with_details, quantize_notes


def notes_to_midi_objects(notes: list[dict]) -> list[MidiNote]:
    """Convert raw note dicts from transcribe step to MidiNote dataclasses."""
    return [
        MidiNote(
            pitch=n["pitch"],
            start=n["start"],
            end=n["end"],
            velocity=n.get("velocity", 80),
        )
        for n in notes
    ]


def midi_to_guitar_tab(
    notes: list[dict],
    tuning: str = "EADGBE",
    tempo_bpm: float = 120.0,
) -> tuple[list[FretPosition], float]:
    """Full pipeline: parse notes → quantize → solve fretboard.

    Returns (positions, ambiguity_score).
    """
    midi_notes = notes_to_midi_objects(notes)
    quantized = quantize_notes(midi_notes, tempo_bpm)
    positions, ambiguity = solve_with_details(quantized, tuning)
    return positions, ambiguity
