import os
import boto3
from fastapi import UploadFile
from app.config import settings


class StorageService:
    """Stores uploaded files in S3 when AWS credentials are configured,
    otherwise falls back to the local filesystem (useful for local/dev runs)."""

    def __init__(self):
        self.use_s3 = bool(settings.aws_access_key_id and settings.aws_secret_access_key)
        self.bucket = settings.aws_bucket
        self.local_root = os.environ.get("LOCAL_STORAGE_DIR", "/data/uploads")
        if self.use_s3:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
            )
        else:
            os.makedirs(self.local_root, exist_ok=True)

    def _local_path(self, key: str) -> str:
        path = os.path.join(self.local_root, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    async def upload(self, file: UploadFile, key: str) -> str:
        content = await file.read()
        if self.use_s3:
            self.s3.put_object(
                Bucket=self.bucket, Key=key, Body=content, ContentType=file.content_type
            )
        else:
            with open(self._local_path(key), "wb") as f:
                f.write(content)
        return key

    def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        if self.use_s3:
            return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires,
            )
        return self._local_path(key)

    def download(self, key: str) -> bytes:
        if self.use_s3:
            resp = self.s3.get_object(Bucket=self.bucket, Key=key)
            return resp["Body"].read()
        with open(self._local_path(key), "rb") as f:
            return f.read()

    def delete(self, key: str) -> None:
        if self.use_s3:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        else:
            try:
                os.remove(self._local_path(key))
            except FileNotFoundError:
                pass

    async def trigger_processing(self, doc_id: str) -> None:
        from app.tasks.tasks import process_document

        process_document.delay(doc_id)
