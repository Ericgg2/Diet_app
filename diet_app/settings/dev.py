# settings/dev.py
from .common import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 개발 환경에서 사용될 데이터베이스 (MySQL 예시)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'diet-board',
        'USER': 'root',
        'PASSWORD': '0000',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# 개발 환경에서는 비밀 키를 그대로 사용 (주의)
SECRET_KEY = "django-insecure-pe*w9s)$flf$59x_r2drbz4&7i)pp467lnvbt8ez3*bf(!*_au"
