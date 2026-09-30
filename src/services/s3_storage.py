import boto3
from botocore.exceptions import ClientError
from src.utils.logger import get_logger

logger = get_logger(__name__)

class S3StorageService:
    def __init__(self, settings):
        self.bucket_name = settings.s3_bucket_name
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )

    def upload_file(self, file_content: bytes, filename: str) -> str:
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=filename, Body=file_content)
            logger.info(f"File {filename} uploaded to S3 bucket {self.bucket_name}")
            return filename
        except ClientError as e:
            logger.error(f"Failed to upload {filename} to S3: {e}")
            raise

    def download_file(self, s3_key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to download {s3_key} from S3: {e}")
            raise

    def list_files(self) -> list[dict]:
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name)
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'filename': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat() if hasattr(obj['LastModified'], 'isoformat') else str(obj['LastModified'])
                    })
            return files
        except ClientError as e:
            logger.error(f"Failed to list files from S3: {e}")
            raise

    def delete_file(self, s3_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"File {s3_key} deleted from S3 bucket {self.bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {s3_key} from S3: {e}")
            raise

    def get_file_url(self, s3_key: str) -> str:
        try:
            url = self.client.generate_presigned_url('get_object',
                                                     Params={'Bucket': self.bucket_name,
                                                             'Key': s3_key},
                                                     ExpiresIn=3600)
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            raise
