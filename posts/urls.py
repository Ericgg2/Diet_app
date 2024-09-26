from django.urls import path
from .views import PostCreateAPIView, PostDetailAPIView, PostListAPIView, MyPostListAPIView

urlpatterns = [
    path('', PostListAPIView.as_view(), name='post_list'),  # 모든 유저의 게시글 목록
    path('myposts/', MyPostListAPIView.as_view(), name='my_post_list'),  # 현재 유저의 게시글 목록
    path('create/', PostCreateAPIView.as_view(), name='create_post'),
    path('detail/<int:pk>/', PostDetailAPIView.as_view(), name='post_detail'),
]
