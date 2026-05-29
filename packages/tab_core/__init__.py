"""tab-core: guitar fretboard solving, tuning, quantization, and tab rendering."""

from .tuning import resolve_tuning, possible_positions, STANDARD_GUITAR, MAX_FRET
from .fretboard import MidiNote, FretPosition, solve, solve_with_details
from .quantize import quantize_notes
from .tab_render import render_ascii_tab, bars_to_ascii, bars_to_json, TabBar

__all__ = [
    "resolve_tuning",
    "possible_positions",
    "STANDARD_GUITAR",
    "MAX_FRET",
    "MidiNote",
    "FretPosition",
    "solve",
    "solve_with_details",
    "quantize_notes",
    "render_ascii_tab",
    "bars_to_ascii",
    "bars_to_json",
    "TabBar",
]
