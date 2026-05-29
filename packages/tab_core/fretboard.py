"""Fretboard solver — the heart of TabSnap.

Given a list of MIDI notes with timing, find the most playable
string/fret assignments on a guitar neck.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .tuning import possible_positions, resolve_tuning, MAX_FRET


@dataclass
class MidiNote:
    pitch: int
    start: float
    end: float
    velocity: int = 80


@dataclass
class FretPosition:
    string: int
    fret: int
    start: float
    end: float


# --- Scoring weights ---
FRET_DISTANCE_WEIGHT = 1.0
STRING_CHANGE_WEIGHT = 0.6
POSITION_SHIFT_WEIGHT = 0.8
OPEN_STRING_BONUS = -0.2  # slight preference for open strings on slow passages
HIGH_FRET_PENALTY_WEIGHT = 0.3
HIGH_FRET_THRESHOLD = 9


def _score_candidate(
    candidate: tuple[int, int],
    prev: tuple[int, int] | None,
    tempo_factor: float = 1.0,
) -> float:
    """Score a (string, fret) candidate relative to the previous position.

    Lower score = better choice.
    """
    s, f = candidate
    score = 0.0

    if prev is not None:
        ps, pf = prev
        # Fret distance
        score += abs(f - pf) * FRET_DISTANCE_WEIGHT
        # String change
        if s != ps:
            score += abs(s - ps) * STRING_CHANGE_WEIGHT
        # Large position shift
        if abs(f - pf) > 4:
            score += (abs(f - pf) - 4) * POSITION_SHIFT_WEIGHT

    # Open string: small bonus for slow passages, no bonus for fast runs
    if f == 0:
        score += OPEN_STRING_BONUS * tempo_factor

    # High fret penalty
    if f > HIGH_FRET_THRESHOLD:
        score += (f - HIGH_FRET_THRESHOLD) * HIGH_FRET_PENALTY_WEIGHT

    return score


def solve(
    notes: Sequence[MidiNote],
    tuning_name: str = "EADGBE",
) -> list[FretPosition]:
    """Assign each MIDI note to the best (string, fret) position.

    Uses a greedy approach with look-ahead scoring.
    Returns a FretPosition for each input note.
    """
    tuning = resolve_tuning(tuning_name)
    result: list[FretPosition] = []
    prev_pos: tuple[int, int] | None = None

    for note in notes:
        candidates = possible_positions(note.pitch, tuning)
        if not candidates:
            # Note out of range — clamp to nearest feasible
            result.append(FretPosition(string=1, fret=0, start=note.start, end=note.end))
            continue

        # Score each candidate
        best = min(candidates, key=lambda c: _score_candidate(c, prev_pos))
        s, f = best
        result.append(FretPosition(string=s, fret=f, start=note.start, end=note.end))
        prev_pos = best

    return result


def solve_with_details(
    notes: Sequence[MidiNote],
    tuning_name: str = "EADGBE",
) -> tuple[list[FretPosition], float]:
    """Solve and return (positions, avg_ambiguity_score).

    Ambiguity = average number of candidate positions per note.
    Higher ambiguity → lower confidence in fretboard assignment.
    """
    tuning = resolve_tuning(tuning_name)
    positions = solve(notes, tuning_name)
    total_candidates = 0
    for note in notes:
        total_candidates += len(possible_positions(note.pitch, tuning))
    avg_ambiguity = total_candidates / max(1, len(notes))
    return positions, avg_ambiguity
