"""TabSnap worker — processes transcription jobs.

With Redis: rq worker tabsnap --url redis://localhost:6379/0
Without Redis: called directly by the API in local dev mode.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure packages are importable
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "packages"))

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SaSession

from pipeline.normalize import normalize_audio
from pipeline.fingerprint import fingerprint_audio
from pipeline.separate import separate_stems
from pipeline.transcribe import transcribe_to_midi
from pipeline.beat import detect_tempo_and_beats
from pipeline.midi_to_tab import midi_to_guitar_tab
from pipeline.confidence import score_confidence
from pipeline.export import export_text_tab

from tab_core import render_ascii_tab, bars_to_ascii, bars_to_json

# Sync engine — Postgres in prod, SQLite locally
DATABASE_URL = os.getenv("DATABASE_URL_SYNC", "")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    _db_path = _root / "data" / "tabsnap.db"
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{_db_path}")

OUTPUT_BASE = Path(os.getenv("OUTPUT_DIR", "data/outputs"))


def _update_stage(session: SaSession, job_id: str, stage: str, progress: int) -> None:
    session.execute(
        sa.text(
            "UPDATE audio_jobs SET stage = :stage, progress = :progress, "
            "status = 'processing', updated_at = now() WHERE id = :id"
        ),
        {"stage": stage, "progress": progress, "id": job_id},
    )
    session.commit()


def _fail_job(session: SaSession, job_id: str, error: str) -> None:
    session.execute(
        sa.text(
            "UPDATE audio_jobs SET status = 'failed', stage = :error, "
            "updated_at = now() WHERE id = :id"
        ),
        {"error": error[:200], "id": job_id},
    )
    session.commit()


def process_job(job_id: str) -> None:
    """Main pipeline — called by RQ."""
    output_dir = OUTPUT_BASE / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    with SaSession(engine) as session:
        row = session.execute(
            sa.text("SELECT file_path, tuning FROM audio_jobs WHERE id = :id"),
            {"id": job_id},
        ).mappings().first()

        if not row:
            raise ValueError(f"Job {job_id} not found")

        file_path = row["file_path"]
        tuning = row["tuning"] or "EADGBE"

        try:
            # Step 1: Normalize
            _update_stage(session, job_id, "normalizing_audio", 10)
            wav_path = normalize_audio(file_path, output_dir)

            # Step 2: Fingerprint (MVP: no-op)
            _update_stage(session, job_id, "fingerprinting", 20)
            song_match = fingerprint_audio(wav_path)

            # Step 3: Stem separation (MVP: pass-through)
            _update_stage(session, job_id, "separating_stems", 35)
            stems = separate_stems(wav_path, output_dir)
            guitar_candidate = stems.get("other", wav_path)

            # Step 4: Transcribe to MIDI
            _update_stage(session, job_id, "transcribing_notes", 55)
            midi_path, notes = transcribe_to_midi(guitar_candidate, output_dir)

            # Step 5: Detect tempo
            _update_stage(session, job_id, "detecting_tempo", 65)
            tempo_bpm, beats = detect_tempo_and_beats(guitar_candidate)

            # Step 6: Build tab
            _update_stage(session, job_id, "building_tab", 80)
            positions, ambiguity = midi_to_guitar_tab(notes, tuning, tempo_bpm)
            bars = render_ascii_tab(positions, tempo_bpm)
            ascii_tab = bars_to_ascii(bars)
            tab_json = bars_to_json(bars)

            # Step 7: Score confidence
            _update_stage(session, job_id, "scoring_confidence", 90)
            confidence = score_confidence(notes, ambiguity, tempo_bpm)

            # Assign confidence to bars
            for bar_data in tab_json.get("bars", []):
                bar_data["confidence"] = confidence["overall"]

            # Step 8: Export text tab
            export_text_tab(ascii_tab, output_dir)

            # Step 9: Save results to DB
            # Song match (if any)
            if song_match:
                session.execute(
                    sa.text(
                        "INSERT INTO song_matches (id, job_id, title, artist, external_id, confidence, provider) "
                        "VALUES (gen_random_uuid(), :job_id, :title, :artist, :ext_id, :conf, :provider)"
                    ),
                    {
                        "job_id": job_id,
                        "title": song_match.get("title"),
                        "artist": song_match.get("artist"),
                        "ext_id": song_match.get("external_id"),
                        "conf": song_match.get("confidence"),
                        "provider": song_match.get("provider"),
                    },
                )

            # Transcription record
            session.execute(
                sa.text(
                    "INSERT INTO transcriptions (id, job_id, tempo_bpm, chords_json, midi_path, "
                    "tab_json, ascii_tab, confidence) "
                    "VALUES (gen_random_uuid(), :job_id, :tempo, :chords, :midi, :tab, :ascii, :conf)"
                ),
                {
                    "job_id": job_id,
                    "tempo": tempo_bpm,
                    "chords": json.dumps([]),  # MVP: chord detection not yet implemented
                    "midi": midi_path,
                    "tab": json.dumps(tab_json),
                    "ascii": ascii_tab,
                    "conf": confidence["overall"],
                },
            )

            # Mark done
            _update_stage(session, job_id, "done", 100)
            session.execute(
                sa.text("UPDATE audio_jobs SET status = 'done', updated_at = now() WHERE id = :id"),
                {"id": job_id},
            )
            session.commit()

        except Exception as exc:
            _fail_job(session, job_id, str(exc))
            raise
