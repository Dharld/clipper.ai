import enum
from sqlalchemy import (Column, String, Float, Boolean, Integer, Text, Enum, ForeignKey, JSON, TIMESTAMP)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class ProjectStatus(enum.Enum):
    queued = "queued"
    processing = "processing"
    preview_ready = "preview_ready"
    exporting = "exporting"
    done = "done"
    failed = "failed"


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    source_video_url = Column(String, nullable=True)
    duration_sec = Column(Float, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.queued)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())


class ClipState(enum.Enum):
    suggested = "suggested"
    kept = "kept"
    discarded = "discarded"
    exported = "exported"


class Clip(Base):
    __tablename__ = "clips"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    start_sec = Column(Float, nullable=False)
    end_sec = Column(Float, nullable=False)
    title = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    snapped_to_pause = Column(Boolean, default=False)
    preview_url = Column(String, nullable=True)
    final_url = Column(String, nullable=True)
    state = Column(Enum(ClipState), default=ClipState.suggested)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())


class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    provider = Column(String, nullable=True)
    language = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    segments = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SilenceMap(Base):
    __tablename__ = "silence_maps"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    silences = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    type = Column(String, nullable=False)  # audio|preview|final
    s3_url = Column(String, nullable=True)
    meta = Column(JSON, nullable=True)
    ttl_days = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
