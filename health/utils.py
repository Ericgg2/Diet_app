import boto3
from botocore.client import Config
import os

# Cloudflare R2 설정 로드
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
R2_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL')  # 예: 'https://<ACCOUNT_ID>.r2.cloudflarestorage.com'

# R2 클라이언트 설정
s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def upload_to_r2(file, file_name):
    """
    Cloudflare R2에 파일을 업로드하고 URL을 반환합니다.
    """
    try:
        # 버킷에 파일 업로드
        s3_client.upload_fileobj(
            file,
            R2_BUCKET_NAME,
            file_name,
            ExtraArgs={'ACL': 'public-read'}  # 파일을 공개적으로 읽을 수 있도록 설정
        )
        # 업로드된 파일의 URL 생성
        file_url = f"{R2_ENDPOINT_URL}/{R2_BUCKET_NAME}/{file_name}"
        return file_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None
