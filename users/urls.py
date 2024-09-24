from django.urls import path
from .views import signup_view, login_view, ProfileListCreateView, ProfileDetailView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('profile/', ProfileListCreateView.as_view(), name='profile-list'),  # 전체 프로필 목록 조회
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),  # 특정 프로필 조회
    path('login/', login_view, name='login'),

]
