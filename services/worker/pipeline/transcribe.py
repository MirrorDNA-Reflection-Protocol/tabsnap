"""Audio-to-MIDI transcription using Basic Pitch."""

from __future__ import annotations

from pathlib import Path


def transcribe_to_midi(wav_path: str, output_dir: Path) -> tuple[str, list[dict]]:
    """Run Basic Pitch on a WAV file.

    Returns (midi_path, notes) where notes is a list of
    {"pitch": int, "start": float, "end": float, "velocity": int, "confidence": float}.
    """
    from basic_pitch.inference import predict
    import pretty_midi

    midi_path = str(output_dir / "output.mid")

    # Basic Pitch predict returns (model_output, midi_data, note_events)
    _model_output, midi_data, note_events = predict(wav_path)

    # Save MIDI file
    midi_data.write(midi_path)

    # Parse note events into our format
    # note_events is a list of (start_time, end_time, pitch, velocity, [confidence])
    notes = []
    for event in note_events:
        start_time = float(event[0])
        end_time = float(event[1])
        pitch = int(event[2])
        velocity = int(event[3]) if len(event) > 3 else 80
        confidence = float(event[4]) if len(event) > 4 else 0.5

        notes.append({
            "pitch": pitch,
            "start": round(start_time, 6),
            "end": round(end_time, 6),
            "velocity": velocity,
            "confidence": confidence,
        })

    # Sort by start time
    notes.sort(key=lambda n: (n["start"], n["pitch"]))

    return midi_path, notes
