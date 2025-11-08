import dramatiq
from dramatiq.brokers.redis import RedisBroker
import os
from .db import SessionLocal
from .models import Project, Asset
from . import storage
import tempfile
import subprocess
import shutil
import uuid

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker = RedisBroker(url=REDIS_URL)
dramatiq.set_broker(broker)


@dramatiq.actor
def process_project(project_id: str):
    """Toy worker that simulates processing and updates project status in DB."""
    session = SessionLocal()
    try:
        proj = session.get(Project, project_id)
        if not proj:
            # create a project record for toy demo
            proj = Project(id=project_id, status="processing")
            session.add(proj)
            session.commit()
        else:
            proj.status = "processing"
            session.commit()

        # Simulate work (real pipeline would run ffmpeg, whisper, etc.)
        import time
        time.sleep(2)

        proj.status = "preview_ready"
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@dramatiq.actor
def audio_extract(project_id: str):
    """Download source video from MinIO, extract audio via ffmpeg, upload audio asset, and record in DB.

    This actor assumes the project's `filename` and `source_video_url` follow the uploader's convention
    (uploads/{project_id}/source/{filename}).
    """
    session = SessionLocal()
    try:
        proj = session.get(Project, project_id)
        if not proj:
            return

        if not proj.source_video_url or not proj.filename:
            proj.error_message = "missing source video"
            proj.status = "failed"
            session.commit()
            return

        # Derive bucket/key - we use the known uploads layout
        bucket = "uploads"
        key = f"{project_id}/source/{proj.filename}"

        tmpdir = tempfile.mkdtemp(prefix=f"clipper_{project_id}_")
        try:
            video_path = os.path.join(tmpdir, "source")
            audio_path = os.path.join(tmpdir, "audio.wav")

            # Download object from MinIO
            s3 = storage.get_s3_client()
            with open(video_path, "wb") as f:
                s3.download_fileobj(bucket, key, f)

            # Extract audio with ffmpeg (mono, 16k PCM WAV)
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                audio_path,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Upload extracted audio
            audio_key = f"{project_id}/audio/audio.wav"
            with open(audio_path, "rb") as af:
                storage.upload_fileobj(bucket, audio_key, af, content_type="audio/wav")

            audio_url = storage.object_s3_url(bucket, audio_key)

            # Record asset in DB
            asset = Asset(
                id="ast_" + uuid.uuid4().hex[:12],
                project_id=project_id,
                type="audio",
                s3_url=audio_url,
                meta={},
            )
            session.add(asset)
            session.commit()

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    except Exception:
        session.rollback()
        # mark project failed if present
        try:
            p = session.get(Project, project_id)
            if p:
                p.status = "failed"
                p.error_message = "audio extraction failed"
                session.commit()
        except Exception:
            session.rollback()
        raise
    finally:
        session.close()
