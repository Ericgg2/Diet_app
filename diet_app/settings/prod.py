# settings/prod.py
from .common import *

DEBUG = False

ALLOWED_HOSTS = ['your-production-domain.com']

# 운영 환경 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'prod_diet_board',
        'USER': 'prod_user',
        'PASSWORD': 'prod_password',
        'HOST': 'prod_db_host',
        'PORT': '3306',
    }
}

# 운영 환경에서 사용하는 비밀 키는 환경 변수로 관리
import os
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-secret-key')

# 기타 운영 환경 관련 설정 (예: 보안 강화)
SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
