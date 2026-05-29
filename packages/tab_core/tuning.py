"""Guitar tuning definitions and helpers."""

from __future__ import annotations

# MIDI note numbers for standard tuning (string 6=low E to string 1=high E)
STANDARD_GUITAR: dict[int, int] = {
    6: 40,  # E2
    5: 45,  # A2
    4: 50,  # D3
    3: 55,  # G3
    2: 59,  # B3
    1: 64,  # E4
}

TUNING_PRESETS: dict[str, dict[int, int]] = {
    "EADGBE": STANDARD_GUITAR,
    "DADGBE": {6: 38, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64},  # Drop D
    "DGDGBE": {6: 38, 5: 43, 4: 50, 3: 55, 2: 59, 1: 64},  # Open G
    "DADF#AD": {6: 38, 5: 45, 4: 50, 3: 54, 2: 57, 1: 62},  # Open D
}

MAX_FRET = 15  # MVP constraint


def resolve_tuning(name: str) -> dict[int, int]:
    """Return string→midi map for a named tuning."""
    key = name.upper().replace(" ", "")
    if key in TUNING_PRESETS:
        return TUNING_PRESETS[key]
    return STANDARD_GUITAR


def possible_positions(midi_note: int, tuning: dict[int, int]) -> list[tuple[int, int]]:
    """Return all (string, fret) pairs that can produce a given MIDI note."""
    positions = []
    for string_num, open_pitch in tuning.items():
        fret = midi_note - open_pitch
        if 0 <= fret <= MAX_FRET:
            positions.append((string_num, fret))
    return positions
