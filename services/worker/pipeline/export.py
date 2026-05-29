"""Export helpers — write MIDI and text tab to output directory."""

from __future__ import annotations

from pathlib import Path


def export_text_tab(ascii_tab: str, output_dir: Path) -> str:
    """Write ASCII tab to a .txt file. Returns the file path."""
    path = output_dir / "tab.txt"
    path.write_text(ascii_tab, encoding="utf-8")
    return str(path)
