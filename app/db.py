import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://clipforge:clipforge@localhost:5432/clipforge")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    # Import models so metadata is registered with SQLAlchemy
    from . import models  # noqa: F401
    models.Base.metadata.create_all(bind=engine)
