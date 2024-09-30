from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Post, Like
from .serializers import PostSerializer, CommentSerializer, PostDetailSerializer
from django.shortcuts import get_object_or_404
from django.db.models import DateField
from django.db.models.functions import TruncDate
from health.models import FoodUpload
from django.db.models import Sum


class PostListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_at')  # 모든 게시글을 가져오고, 작성일 기준으로 내림차순 정렬
        serializer = PostDetailSerializer(posts, many=True)  # 직렬화
        return Response(serializer.data)


class MyPostListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 현재 유저의 게시글을 날짜별로 그룹화하고, 같은 날짜는 작성 순서로 정렬
        posts = Post.objects.filter(user=request.user).annotate(
            date=TruncDate('created_at')  # created_at에서 날짜만 추출
        ).order_by('-date', 'created_at')  # 날짜별로 내림차순 정렬 후, 같은 날짜는 작성 순서로 정렬

        serializer = PostDetailSerializer(posts, many=True)  # 직렬화
        return Response(serializer.data)


class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 사용자가 선택한 FoodUpload ID 목록과 캡션을 받음
        food_upload_ids = request.data.get('food_uploads', [])
        caption = request.data.get('caption', '')

        # FoodUpload 객체들 가져오기
        food_uploads = FoodUpload.objects.filter(id__in=food_upload_ids, user=request.user)

        if not food_uploads:
            return Response({"error": "음식 업로드 기록이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 총 영양성분 계산
        total_calories = food_uploads.aggregate(Sum('calories'))['calories__sum'] or 0
        total_protein = food_uploads.aggregate(Sum('protein'))['protein__sum'] or 0
        total_fat = food_uploads.aggregate(Sum('fat'))['fat__sum'] or 0
        total_carbs = food_uploads.aggregate(Sum('carbs'))['carbs__sum'] or 0

        # 사용자 목표 가져오기
        user_goal = request.user.usergoal

        # 목표와의 차이 계산 및 결과 결정
        result = "성공" if total_calories <= user_goal.daily_calories else "실패"

        # 게시글 생성
        post = Post.objects.create(
            user=request.user,
            total_calories=total_calories,
            total_protein=total_protein,
            total_fat=total_fat,
            total_carbs=total_carbs,
            goal_calories=user_goal.daily_calories,
            goal_protein=user_goal.protein_goal,
            goal_fat=user_goal.fat_goal,
            goal_carbs=user_goal.carbs_goal,
            result=result,
            caption=caption
        )

        # 선택한 음식 업로드들 연결
        post.food_uploads.set(food_uploads)
        post.save()

        return Response({"message": "게시글이 성공적으로 업로드되었습니다."}, status=status.HTTP_201_CREATED)

class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)  # pk로 특정 게시글을 가져옴
        serializer = PostDetailSerializer(post, context={'request': request})  # 요청 컨텍스트 전달
        return Response(serializer.data)

    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)  # 댓글을 달기 위해 게시글을 가져옴
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)  # 게시글 가져오기
        like, created = Like.objects.get_or_create(user=request.user, post=post)  # 좋아요 추가

        if created:
            return Response({"message": "좋아요를 눌렀습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)  # 게시글 가져오기
        try:
            like = Like.objects.get(user=request.user, post=post)  # 좋아요 가져오기
            like.delete()  # 좋아요 삭제
            return Response({"message": "좋아요가 해제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({"message": "먼저 좋아요를 눌러주세요."}, status=status.HTTP_400_BAD_REQUEST)

    def calculate_calories(self, grams):
        return grams  # Example: 2 calories per gram

    def get_feedback(self, remaining_calories):
        if remaining_calories < 0:
            return "칼로리를 초과했습니다. 조절하세요."
        return "영양소 섭취가 적절합니다."





