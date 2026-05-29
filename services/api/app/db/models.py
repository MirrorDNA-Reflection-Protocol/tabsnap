"""SQLAlchemy models matching the spec's Postgres schema."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> uuid.UUID:
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    email = Column(Text, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    jobs = relationship("AudioJob", back_populates="user")
    corrections = relationship("Correction", back_populates="user")


class AudioJob(Base):
    __tablename__ = "audio_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    original_filename = Column(Text)
    file_path = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="queued")
    stage = Column(String(64), nullable=True)
    progress = Column(Integer, default=0)
    instrument = Column(String(32), default="guitar")
    tuning = Column(String(32), default="EADGBE")
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="jobs")
    song_match = relationship("SongMatch", back_populates="job", uselist=False)
    transcription = relationship("Transcription", back_populates="job", uselist=False)
    corrections = relationship("Correction", back_populates="job")


class SongMatch(Base):
    __tablename__ = "song_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    job_id = Column(UUID(as_uuid=True), ForeignKey("audio_jobs.id"), nullable=False)
    title = Column(Text)
    artist = Column(Text)
    external_id = Column(Text)
    confidence = Column(Float)
    provider = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    job = relationship("AudioJob", back_populates="song_match")


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    job_id = Column(UUID(as_uuid=True), ForeignKey("audio_jobs.id"), nullable=False)
    tempo_bpm = Column(Float)
    key_signature = Column(String(16))
    chords_json = Column(JSONB)
    midi_path = Column(Text)
    tab_json = Column(JSONB)
    ascii_tab = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    job = relationship("AudioJob", back_populates="transcription")


class Correction(Base):
    __tablename__ = "corrections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_new_id)
    job_id = Column(UUID(as_uuid=True), ForeignKey("audio_jobs.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    corrected_tab = Column(Text)
    notes = Column(Text)
    rating = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    job = relationship("AudioJob", back_populates="corrections")
    user = relationship("User", back_populates="corrections")
