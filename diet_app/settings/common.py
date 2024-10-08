# settings/common.py
from pathlib import Path
import os
import boto3

from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

BASE_DIR = Path(__file__).resolve().parent.parent.parent


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 공통 설정
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "users",
    "posts",
    "health",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "diet_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "diet_app.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from datetime import timedelta

# JWT 설정
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=180),  # 액세스 토큰의 유효 기간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # 리프레시 토큰의 유효 기간
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your_secret_key',  # 운영환경에선 환경변수를 통해 관리하는 것이 좋습니다.
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# # Cloudflare R2 Access 설정
# AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')  # 환경변수로 설정
# AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')  # 환경변수로 설정
# AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')  # 버킷 이름
# AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

# # Cloudflare R2의 커스텀 엔드포인트 설정
# AWS_S3_ENDPOINT_URL = 'https://5fb2ad66dc77b486be78e8a6c1543b1d.r2.cloudflarestorage.com'  # Cloudflare R2의 계정 ID를 사용
# AWS_S3_REGION_NAME = 'auto'  # Cloudflare R2의 기본 리전 설정

# # 파일을 R2 버킷에 저장하도록 설정
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# MEDIA_URL = 'https://5fb2ad66dc77b486be78e8a6c1543b1d.r2.cloudflarestorage.com/diet-control-app/'

# # Cloudflare R2 미디어 URL 설정
