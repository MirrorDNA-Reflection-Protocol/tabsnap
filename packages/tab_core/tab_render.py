"""Render fretboard positions into ASCII guitar tab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .fretboard import FretPosition

# String labels from high E (1) to low E (6)
STRING_LABELS = {1: "e", 2: "B", 3: "G", 4: "D", 5: "A", 6: "E"}

CHARS_PER_BEAT = 4  # horizontal resolution


@dataclass
class TabBar:
    bar_index: int
    time_start: float
    time_end: float
    lines: list[str]
    confidence: float = 0.0


def render_ascii_tab(
    positions: Sequence[FretPosition],
    tempo_bpm: float = 120.0,
    beats_per_bar: int = 4,
) -> list[TabBar]:
    """Convert fretboard positions into bars of ASCII tab.

    Each bar spans `beats_per_bar` beats at the given tempo.
    """
    if not positions:
        return []

    beat_duration = 60.0 / max(tempo_bpm, 30)
    bar_duration = beat_duration * beats_per_bar
    bar_width = beats_per_bar * CHARS_PER_BEAT

    # Determine total time span
    t_min = min(p.start for p in positions)
    t_max = max(p.end for p in positions)
    total_bars = max(1, int((t_max - t_min) / bar_duration) + 1)

    bars: list[TabBar] = []
    for bar_idx in range(total_bars):
        bar_start = t_min + bar_idx * bar_duration
        bar_end = bar_start + bar_duration

        # Initialize empty string lines
        grid: dict[int, list[str]] = {}
        for s in range(1, 7):
            grid[s] = ["-"] * bar_width

        # Place notes in this bar
        for pos in positions:
            if pos.end <= bar_start or pos.start >= bar_end:
                continue
            # Calculate horizontal position within bar
            offset = (pos.start - bar_start) / bar_duration
            col = int(offset * bar_width)
            col = max(0, min(col, bar_width - 1))

            fret_str = str(pos.fret)
            if pos.string in grid:
                # Write fret number (may be 2 digits)
                for i, ch in enumerate(fret_str):
                    if col + i < bar_width:
                        grid[pos.string][col + i] = ch

        lines = []
        for s in range(1, 7):
            label = STRING_LABELS[s]
            body = "".join(grid[s])
            lines.append(f"{label}|{body}|")

        bars.append(TabBar(
            bar_index=bar_idx + 1,
            time_start=round(bar_start, 3),
            time_end=round(bar_end, 3),
            lines=lines,
        ))

    return bars


def bars_to_ascii(bars: Sequence[TabBar]) -> str:
    """Join all bars into a single multi-line ASCII tab string."""
    sections = []
    for bar in bars:
        sections.append("\n".join(bar.lines))
    return "\n\n".join(sections)


def bars_to_json(bars: Sequence[TabBar]) -> dict:
    """Serialize bars for the API response."""
    return {
        "format": "ascii",
        "bars": [
            {
                "bar_index": b.bar_index,
                "time_start": b.time_start,
                "time_end": b.time_end,
                "confidence": b.confidence,
                "lines": b.lines,
            }
            for b in bars
        ],
    }
