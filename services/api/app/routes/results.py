"""GET /api/jobs/{job_id}/result – transcription output."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import AudioJob
from app.db.session import get_db

router = APIRouter(tags=["results"])


@router.get("/jobs/{job_id}/result")
async def get_result(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AudioJob)
        .where(AudioJob.id == job_id)
        .options(
            selectinload(AudioJob.song_match),
            selectinload(AudioJob.transcription),
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")
    if job.status != "done":
        raise HTTPException(409, f"Job not ready. Current status: {job.status}")

    tx = job.transcription
    if not tx:
        raise HTTPException(500, "Transcription record missing")

    sm = job.song_match
    song_match = None
    if sm:
        song_match = {
            "found": True,
            "title": sm.title,
            "artist": sm.artist,
            "confidence": sm.confidence,
        }
    else:
        song_match = {"found": False, "title": None, "artist": None, "confidence": 0}

    return {
        "job_id": str(job.id),
        "song_match": song_match,
        "tempo_bpm": tx.tempo_bpm,
        "key_signature": tx.key_signature,
        "tuning": job.tuning,
        "chords": tx.chords_json or [],
        "tab": tx.tab_json or {"format": "ascii", "bars": []},
        "ascii_tab": tx.ascii_tab,
        "confidence": tx.confidence,
        "midi_url": f"/files/{job.id}/output.mid" if tx.midi_path else None,
        "audio_preview_url": f"/files/{job.id}/preview.wav",
    }
