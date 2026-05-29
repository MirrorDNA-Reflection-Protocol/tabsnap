"""Audio-to-MIDI transcription.

Uses Basic Pitch when available (best quality).
Falls back to librosa pitch tracking (lighter, no TensorFlow needed).
"""

from __future__ import annotations

from pathlib import Path

HAS_BASIC_PITCH = False
try:
    from basic_pitch.inference import predict as bp_predict
    HAS_BASIC_PITCH = True
except ImportError:
    pass


def transcribe_to_midi(wav_path: str, output_dir: Path) -> tuple[str, list[dict]]:
    """Transcribe audio to MIDI notes.

    Returns (midi_path, notes) where notes is a list of
    {"pitch": int, "start": float, "end": float, "velocity": int, "confidence": float}.
    """
    if HAS_BASIC_PITCH:
        return _transcribe_basic_pitch(wav_path, output_dir)
    return _transcribe_librosa(wav_path, output_dir)


def _transcribe_basic_pitch(wav_path: str, output_dir: Path) -> tuple[str, list[dict]]:
    """High-quality transcription via Basic Pitch (Spotify)."""
    midi_path = str(output_dir / "output.mid")
    _model_output, midi_data, note_events = bp_predict(wav_path)
    midi_data.write(midi_path)

    notes = []
    for event in note_events:
        notes.append({
            "pitch": int(event[2]),
            "start": round(float(event[0]), 6),
            "end": round(float(event[1]), 6),
            "velocity": int(event[3]) if len(event) > 3 else 80,
            "confidence": float(event[4]) if len(event) > 4 else 0.5,
        })
    notes.sort(key=lambda n: (n["start"], n["pitch"]))
    return midi_path, notes


def _transcribe_librosa(wav_path: str, output_dir: Path) -> tuple[str, list[dict]]:
    """Lightweight fallback using librosa pitch tracking + pretty_midi export."""
    import librosa
    import numpy as np
    import pretty_midi

    y, sr = librosa.load(wav_path, sr=44100, mono=True)

    # Pitch tracking with pyin (probabilistic YIN — good for monophonic)
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y, fmin=librosa.note_to_hz("E2"), fmax=librosa.note_to_hz("E6"),
        sr=sr, frame_length=2048,
    )
    times = librosa.times_like(f0, sr=sr)

    # Segment continuous pitched regions into notes
    notes = []
    in_note = False
    note_start = 0.0
    note_pitch = 0
    note_conf = 0.0
    conf_samples = 0

    for i, (freq, voiced, prob) in enumerate(zip(f0, voiced_flag, voiced_prob)):
        t = float(times[i])
        if voiced and not np.isnan(freq) and freq > 0:
            midi_note = int(round(librosa.hz_to_midi(freq)))
            if not in_note:
                in_note = True
                note_start = t
                note_pitch = midi_note
                note_conf = float(prob)
                conf_samples = 1
            elif abs(midi_note - note_pitch) > 1:
                # Pitch changed — close current note, start new
                notes.append({
                    "pitch": note_pitch,
                    "start": round(note_start, 6),
                    "end": round(t, 6),
                    "velocity": 80,
                    "confidence": round(note_conf / max(1, conf_samples), 3),
                })
                note_start = t
                note_pitch = midi_note
                note_conf = float(prob)
                conf_samples = 1
            else:
                note_conf += float(prob)
                conf_samples += 1
        else:
            if in_note:
                notes.append({
                    "pitch": note_pitch,
                    "start": round(note_start, 6),
                    "end": round(t, 6),
                    "velocity": 80,
                    "confidence": round(note_conf / max(1, conf_samples), 3),
                })
                in_note = False

    # Close final note
    if in_note and len(times) > 0:
        notes.append({
            "pitch": note_pitch,
            "start": round(note_start, 6),
            "end": round(float(times[-1]), 6),
            "velocity": 80,
            "confidence": round(note_conf / max(1, conf_samples), 3),
        })

    # Filter very short notes (< 50ms) — likely noise
    notes = [n for n in notes if n["end"] - n["start"] >= 0.05]
    notes.sort(key=lambda n: (n["start"], n["pitch"]))

    # Export MIDI
    midi_path = str(output_dir / "output.mid")
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    guitar = pretty_midi.Instrument(program=25, name="Guitar")
    for n in notes:
        midi_note = pretty_midi.Note(
            velocity=n["velocity"],
            pitch=n["pitch"],
            start=n["start"],
            end=n["end"],
        )
        guitar.notes.append(midi_note)
    pm.instruments.append(guitar)
    pm.write(midi_path)

    return midi_path, notes
