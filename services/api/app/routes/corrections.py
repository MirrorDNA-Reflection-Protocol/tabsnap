"""POST /api/jobs/{job_id}/corrections – save user tab edits."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioJob, Correction
from app.db.session import get_db

router = APIRouter(tags=["corrections"])


class CorrectionIn(BaseModel):
    corrected_tab: str
    notes: str | None = None
    rating: int | None = None


@router.post("/jobs/{job_id}/corrections")
async def save_correction(
    job_id: str,
    body: CorrectionIn,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AudioJob).where(AudioJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")

    correction = Correction(
        job_id=job_id,
        corrected_tab=body.corrected_tab,
        notes=body.notes,
        rating=body.rating,
    )
    db.add(correction)
    await db.commit()
    await db.refresh(correction)

    return {"saved": True, "correction_id": str(correction.id)}
