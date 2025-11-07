import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://clipper:clipper@postgres:5432/clipper")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
