"""
URL configuration for diet_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', include('users.urls')),  # users 앱의 URL 추가
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT 토큰 발급
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 리프레시 토큰으로 액세스 토큰 갱신
    path('health/', include('health.urls')),  # health 앱의 URL 추가
    path('posts/', include('posts.urls')),  # posts 앱의 URL 추가
    
]

if settings.DEBUG:  # DEBUG 모드에서만 media 파일 서빙을 허용
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
