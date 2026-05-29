"""Tempo and beat detection using librosa."""

from __future__ import annotations


def detect_tempo_and_beats(wav_path: str) -> tuple[float, list[float]]:
    """Detect tempo (BPM) and beat positions from a WAV file.

    Returns (tempo_bpm, beat_times_seconds).
    """
    import librosa
    import numpy as np

    y, sr = librosa.load(wav_path, sr=44100, mono=True)

    # Estimate tempo
    tempo_array, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # tempo_array may be a scalar or array depending on librosa version
    tempo = float(np.asarray(tempo_array).flatten()[0])

    # Convert beat frames to time
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    return round(tempo, 1), [round(float(t), 4) for t in beat_times]
