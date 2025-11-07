import dramatiq
from dramatiq.brokers.redis import RedisBroker
import os
from .db import SessionLocal
from .models import Project

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
