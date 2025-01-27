import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.config import settings

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket = settings.aws_bucket

    async def upload(self, file: UploadFile, key: str) -> str:
        content = await file.read()
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=file.content_type)
        return key

    def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires,
        )

    def download(self, key: str) -> bytes:
        resp = self.s3.get_object(Bucket=self.bucket, Key=key)
        return resp["Body"].read()

    def delete(self, key: str) -> None:
        self.s3.delete_object(Bucket=self.bucket, Key=key)

    async def trigger_processing(self, doc_id: str) -> None:
        from app.tasks.tasks import process_document
        process_document.delay(doc_id)
