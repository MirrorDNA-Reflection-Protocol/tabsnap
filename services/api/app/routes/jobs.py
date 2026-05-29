"""POST /api/jobs  &  GET /api/jobs/{job_id} – upload and status."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioJob
from app.db.session import get_db
from app.queue.enqueue import enqueue_transcription
from app.storage.local import save_upload

router = APIRouter(tags=["jobs"])

MAX_DURATION = 30  # seconds — enforced at worker level for MVP


@router.post("/jobs")
async def create_job(
    file: UploadFile = File(...),
    instrument: str = Form("guitar"),
    tuning: str = Form("EADGBE"),
    clip_start_seconds: float | None = Form(None),
    clip_end_seconds: float | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    try:
        job_id, file_path = save_upload(file.filename, file.file)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    job = AudioJob(
        id=job_id,
        original_filename=file.filename,
        file_path=file_path,
        status="queued",
        instrument=instrument,
        tuning=tuning,
    )
    db.add(job)
    await db.commit()

    enqueue_transcription(job_id)

    return {"job_id": job_id, "status": "queued"}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AudioJob).where(AudioJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "job_id": str(job.id),
        "status": job.status,
        "stage": job.stage,
        "progress": job.progress,
    }
