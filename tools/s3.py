import boto3
from botocore.client import Config, ClientError
from tools.settings import settings
import io

s3 = boto3.client('s3',
                    endpoint_url=settings.s3_host,
                    aws_access_key_id=settings.s3_ak,
                    aws_secret_access_key=settings.s3_sk,
                    config=Config(signature_version='s3v4'))

s3_r = boto3.resource('s3',
                    endpoint_url=settings.s3_host,
                    aws_access_key_id=settings.s3_ak,
                    aws_secret_access_key=settings.s3_sk,
                    config=Config(signature_version='s3v4'))

def init_buckets():
    try:
        s3.head_bucket(Bucket="basic")
    except ClientError:
        s3.create_bucket(Bucket="basic")
    s3_r.Bucket("basic").objects.all().delete()
        
def add_file(file, bucket: str, key: str):
    s3.upload_fileobj(file, bucket, key)

def get_file(bucket: str, key: str):
    f = io.BytesIO()
    s3_r.Bucket(bucket).Object(key).download_fileobj(f)
    f.seek(0)
    return f

def get_bytes(bucket: str, key: str):
    f = get_file(bucket, key)
    with f:
        yield from f