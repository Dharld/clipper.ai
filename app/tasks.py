import dramatiq
from dramatiq.brokers.redis import RedisBroker
import os
from .db import SessionLocal
from .models import Project, Asset, Transcript, SilenceMap, Clip, ProjectStatus
from . import storage
import tempfile
import subprocess
import shutil
import uuid
from openai import OpenAI
import time
import random
import logging

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker = RedisBroker(url=REDIS_URL)
dramatiq.set_broker(broker)


@dramatiq.actor
def process_project(project_id: str):
    """Demo worker for testing - simulates processing and updates project status."""
    session = SessionLocal()
    try:
        proj = session.get(Project, project_id)
        if not proj:
            # create a project record for toy demo
            proj = Project(id=project_id, status=ProjectStatus.processing)
            session.add(proj)
            session.commit()
        else:
            proj.status = ProjectStatus.processing
            session.commit()

        # Simulate work (real pipeline would run ffmpeg, whisper, etc.)
        time.sleep(2)

        proj.status = ProjectStatus.preview_ready
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@dramatiq.actor
def silence_map(project_id: str, asset_id: str = None):
    """Run ffmpeg silencedetect on the extracted audio and persist SilenceMap JSON."""
    session = SessionLocal()
    try:
        # find the most recent audio asset if not provided
        if asset_id:
            asset = session.get(Asset, asset_id)
        else:
            asset = session.query(Asset).filter_by(project_id=project_id, type="audio").order_by(Asset.created_at.desc()).first()

        if not asset:
            return

        tmpdir = tempfile.mkdtemp(prefix=f"clipper_sil_{project_id}_")
        try:
            audio_path = os.path.join(tmpdir, "audio.wav")
            # download
            s3 = storage.get_s3_client()
            # derive bucket/key from stored project layout
            # asset.s3_url is like {MINIO_ENDPOINT}/uploads/{project_id}/audio/audio.wav
            parts = asset.s3_url.split('/')
            # find 'uploads' index - treat the bucket as the known 'uploads' bucket
            if 'uploads' in parts:
                idx = parts.index('uploads')
                # keep bucket at the expected top-level 'uploads' bucket
                bucket = 'uploads'
                key = '/'.join(parts[idx+1:])
            else:
                bucket = 'uploads'
                key = f"{project_id}/audio/audio.wav"

            with open(audio_path, 'wb') as f:
                s3.download_fileobj(bucket, key, f)

            cmd = [
                'ffmpeg', '-nostdin', '-i', audio_path, '-af', 'silencedetect=noise=-30dB:d=0.5', '-f', 'null', '-'
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            stderr = proc.stderr or ''

            # parse lines like "silence_start: 12.345" and "silence_end: 15.678"
            silences = []
            cur = None
            for ln in stderr.splitlines():
                ln = ln.strip()
                if 'silence_start:' in ln:
                    try:
                        t = float(ln.split('silence_start:')[-1].strip())
                        cur = {"start_sec": t}
                    except Exception:
                        cur = None
                if 'silence_end:' in ln and cur is not None:
                    try:
                        t = float(ln.split('silence_end:')[-1].split('|')[0].strip())
                        cur['end_sec'] = t
                        silences.append(cur)
                        cur = None
                    except Exception:
                        cur = None

            sm = SilenceMap(id="sil_" + uuid.uuid4().hex[:12], project_id=project_id, silences=silences)
            session.add(sm)
            session.commit()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@dramatiq.actor
def transcribe(project_id: str, asset_id: str):
    """Transcribe audio using OpenAI Whisper or fall back to mock segments."""
    session = SessionLocal()
    logger = logging.getLogger("clipper.tasks.transcribe")
    
    try:
        asset = session.get(Asset, asset_id)
        if not asset:
            logger.warning("Asset %s not found", asset_id)
            return

        tmpdir = tempfile.mkdtemp(prefix=f"clipper_tr_{project_id}_")
        try:
            audio_path = os.path.join(tmpdir, 'audio.wav')
            
            # Download audio from S3
            s3 = storage.get_s3_client()
            parts = asset.s3_url.split('/')
            if 'uploads' in parts:
                idx = parts.index('uploads')
                bucket = 'uploads'
                key = '/'.join(parts[idx+1:])
            else:
                bucket = 'uploads'
                key = f"{project_id}/audio/audio.wav"

            try:
                with open(audio_path, 'wb') as f:
                    s3.download_fileobj(bucket, key, f)
                logger.info("Downloaded audio: %s/%s", bucket, key)
            except Exception as e:
                logger.exception("Failed to download audio: %s/%s", bucket, key)
                proj = session.get(Project, project_id)
                if proj:
                    proj.status = ProjectStatus.failed
                    proj.error_message = f"Audio download failed: {e}"
                    session.commit()
                return

            # Get audio duration
            try:
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                     "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                    capture_output=True, text=True, check=True
                )
                duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0.0
                logger.info("Audio duration: %.2f seconds", duration)
            except Exception:
                logger.exception("ffprobe failed")
                duration = 0.0

            # Try OpenAI Whisper if API key is available
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                proj = session.get(Project, project_id)
                
                # Build transcription prompt
                prompt_from_env = os.getenv("TRANSCRIPTION_PROMPT")
                if prompt_from_env:
                    prompt = prompt_from_env
                else:
                    prompt_parts = [
                        "Transcribe the audio accurately with proper punctuation and capitalization.",
                        "Do not add speaker labels."
                    ]
                    if proj and proj.filename:
                        prompt_parts.insert(0, f"Audio from: {proj.filename}")
                    prompt = " ".join(prompt_parts)

                client = OpenAI(api_key=openai_key)
                max_attempts = int(os.getenv("OPENAI_RETRY_ATTEMPTS", "5"))
                backoff_base = float(os.getenv("OPENAI_RETRY_BACKOFF", "1.0"))
                
                resp = None
                last_exc = None
                
                with open(audio_path, "rb") as af:
                    for attempt in range(1, max_attempts + 1):
                        try:
                            logger.info("OpenAI transcription attempt %d/%d", attempt, max_attempts)
                            resp = client.audio.transcriptions.create(
                                file=af,
                                model="whisper-1",
                                response_format="verbose_json",
                                prompt=prompt
                            )
                            logger.info("OpenAI transcription succeeded")
                            break
                        except Exception as e:
                            last_exc = e
                            errstr = str(e).lower()
                            
                            # Check for quota/billing errors - don't retry
                            if 'insufficient_quota' in errstr or 'quota' in errstr or 'billing' in errstr:
                                logger.error("OpenAI quota/billing error: %s", e)
                                if proj:
                                    proj.status = ProjectStatus.failed
                                    proj.error_message = "OpenAI quota/billing error"
                                    session.commit()
                                return
                            
                            # Check for rate limit
                            is_rate_limit = '429' in str(e) or getattr(e, 'status_code', None) == 429
                            
                            if attempt == max_attempts:
                                logger.error("OpenAI transcription failed after %d attempts", max_attempts)
                                raise
                            
                            sleep = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                            logger.warning(
                                "Attempt %d failed (rate_limit=%s), retrying in %.1fs: %s",
                                attempt, is_rate_limit, sleep, e
                            )
                            time.sleep(sleep)
                            af.seek(0)  # Reset file pointer for retry

                if resp is None:
                    raise last_exc or Exception("No response from OpenAI")

                # Extract data from OpenAI response object (not JSON string!)
                try:
                    # The response object has attributes, not dict keys
                    full_text = resp.text if hasattr(resp, 'text') else ""
                    language = resp.language if hasattr(resp, 'language') else "unknown"
                    
                    # Convert segments to our format
                    segments = []
                    if hasattr(resp, 'segments'):
                        for i, seg in enumerate(resp.segments):
                            segments.append({
                                "id": f"seg_{i}",
                                "start_sec": float(seg.get('start', 0.0) if isinstance(seg, dict) else getattr(seg, 'start', 0.0)),
                                "end_sec": float(seg.get('end', 0.0) if isinstance(seg, dict) else getattr(seg, 'end', 0.0)),
                                "text": (seg.get('text', '') if isinstance(seg, dict) else getattr(seg, 'text', '')).strip(),
                                "confidence": seg.get('avg_logprob') if isinstance(seg, dict) else getattr(seg, 'avg_logprob', None),
                            })
                    else:
                        # Fallback: single segment with full text
                        segments.append({
                            "id": "seg_0",
                            "start_sec": 0.0,
                            "end_sec": duration,
                            "text": full_text,
                            "confidence": None,
                        })

                    tr = Transcript(
                        id="tr_" + uuid.uuid4().hex[:12],
                        project_id=project_id,
                        provider="openai_whisper",
                        language=language,
                        text=full_text,
                        segments=segments
                    )
                    session.add(tr)
                    session.commit()
                    logger.info(
                        "Transcript saved: id=%s provider=openai_whisper segments=%d language=%s",
                        tr.id, len(segments), language
                    )
                    
                    # Enqueue downstream task
                    highlights_pick.send(project_id)
                    
                except Exception as e:
                    logger.exception("Failed to process OpenAI response: %s", e)
                    session.rollback()
                    raise

            else:
                # No OpenAI key - create mock transcript
                logger.info("No OPENAI_API_KEY, creating mock transcript")
                seg_len = 30.0
                segments = []
                idx = 0
                t = 0.0
                while t < duration and idx < 200:
                    end = min(t + seg_len, duration)
                    segments.append({
                        "id": f"seg_{idx}",
                        "start_sec": t,
                        "end_sec": end,
                        "text": f"Mock transcript segment {idx} from {t:.1f}s to {end:.1f}s",
                        "confidence": 0.9,
                    })
                    idx += 1
                    t = end

                tr = Transcript(
                    id="tr_" + uuid.uuid4().hex[:12],
                    project_id=project_id,
                    provider="mock",
                    language="en",
                    text="Mock transcript",
                    segments=segments
                )
                session.add(tr)
                session.commit()
                logger.info("Mock transcript saved: id=%s segments=%d", tr.id, len(segments))
                
                # Enqueue downstream task
                highlights_pick.send(project_id)

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
            
    except Exception as e:
        logger.exception("Transcription task failed for project %s", project_id)
        session.rollback()
        raise
    finally:
        session.close()


@dramatiq.actor
def highlights_pick(project_id: str):
    """Pick candidate clips from transcript segments and create Clip rows."""
    session = SessionLocal()
    try:
        tr = session.query(Transcript).filter_by(project_id=project_id).order_by(Transcript.created_at.desc()).first()
        if not tr or not tr.segments:
            return

        segments = tr.segments
        # score by segment length and pick top 3
        scored = []
        for s in segments:
            length = (s.get('end_sec', 0) or 0) - (s.get('start_sec', 0) or 0)
            scored.append((length, s))
        scored.sort(reverse=True, key=lambda x: x[0])
        picks = [s for (_, s) in scored[:3]]

        clips = []
        for p in picks:
            clip = Clip(id="c_" + uuid.uuid4().hex[:12], project_id=project_id, start_sec=p['start_sec'], end_sec=p['end_sec'], title=None, reason="auto", score=1.0, snapped_to_pause=False, state="suggested")
            session.add(clip)
            clips.append(clip)
        session.commit()

        # enqueue preview render for each clip
        for c in clips:
            preview_render.send(project_id, c.id)

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@dramatiq.actor
def preview_render(project_id: str, clip_id: str):
    """Cut a short preview from the source video for the clip and upload to MinIO, updating the Clip preview_url."""
    session = SessionLocal()
    try:
        clip = session.get(Clip, clip_id)
        proj = session.get(Project, project_id)
        if not clip or not proj:
            return

        tmpdir = tempfile.mkdtemp(prefix=f"clipper_pr_{project_id}_")
        try:
            src_video_path = os.path.join(tmpdir, 'source.mp4')
            out_path = os.path.join(tmpdir, 'preview.mp4')

            # download source video
            bucket = 'uploads'
            key = f"{project_id}/source/{proj.filename}"
            s3 = storage.get_s3_client()
            with open(src_video_path, 'wb') as f:
                s3.download_fileobj(bucket, key, f)

            duration = clip.end_sec - clip.start_sec
            # ffmpeg: seek then copy short segment, re-encode to low bitrate preview
            cmd = [
                'ffmpeg', '-y', '-ss', str(clip.start_sec), '-i', src_video_path, '-t', str(duration), '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '400k', '-c:a', 'aac', '-b:a', '64k', out_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            preview_key = f"{project_id}/previews/{clip_id}.mp4"
            with open(out_path, 'rb') as pf:
                storage.upload_fileobj('uploads', preview_key, pf, content_type='video/mp4')
            preview_url = storage.object_s3_url('uploads', preview_key)

            clip.preview_url = preview_url
            session.commit()

            # update project status
            proj.status = ProjectStatus.preview_ready
            session.commit()

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

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
            proj.status = ProjectStatus.failed
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

            # Get duration via ffprobe and save meta
            try:
                probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path], capture_output=True, text=True)
                duration = float(probe.stdout.strip()) if probe.stdout.strip() else None
            except Exception:
                duration = None

            # Record asset in DB
            asset = Asset(
                id="ast_" + uuid.uuid4().hex[:12],
                project_id=project_id,
                type="audio",
                s3_url=audio_url,
                meta={"duration_sec": duration} if duration else {},
            )
            session.add(asset)
            # update project duration if available
            if duration:
                try:
                    proj.duration_sec = duration
                except Exception:
                    pass
            session.commit()

            # Enqueue downstream workers
            # Silence detection and transcription can run in parallel
            silence_map.send(project_id, asset.id)
            transcribe.send(project_id, asset.id)

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    except Exception:
        session.rollback()
        # mark project failed if present
        try:
            p = session.get(Project, project_id)
            if p:
                p.status = ProjectStatus.failed
                p.error_message = "audio extraction failed"
                session.commit()
        except Exception:
            session.rollback()
        raise
    finally:
        session.close()
