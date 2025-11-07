import os
from urllib.parse import urljoin
import boto3
from botocore.client import Config

from .config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket(bucket_name: str):
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
    except Exception:
        # try to create the bucket (MinIO / local dev)
        s3.create_bucket(Bucket=bucket_name)


def generate_presigned_put(bucket: str, key: str, content_type: str, expires: int = 3600) -> str:
    s3 = get_s3_client()
    params = {"Bucket": bucket, "Key": key, "ContentType": content_type}
    return s3.generate_presigned_url("put_object", Params=params, ExpiresIn=expires)


def object_s3_url(bucket: str, key: str) -> str:
    # Construct a simple HTTP URL for MinIO access. For MinIO the object URL is typically:
    # {MINIO_ENDPOINT}/{bucket}/{key}
    return f"{MINIO_ENDPOINT.rstrip('/')}/{bucket}/{key}"


def upload_fileobj(bucket: str, key: str, fileobj, content_type: str = None):
    """Upload a file-like object to the given bucket/key. `fileobj` should be a file-like
    object (has a read() method). This wraps boto3.upload_fileobj which streams the data.
    """
    s3 = get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type
    # fileobj may be a Starlette UploadFile; get the underlying file-like
    f = getattr(fileobj, "file", fileobj)
    # ensure pointer at start
    try:
        f.seek(0)
    except Exception:
        pass
    s3.upload_fileobj(f, bucket, key, ExtraArgs=extra_args)

