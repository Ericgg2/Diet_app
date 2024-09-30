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
from users.models import UserGoal
from health.models import DailyNutrition
from datetime import date  # date 모듈을 가져옵니다.


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
        title = request.data.get('title', '')
        caption = request.data.get('caption', '')

        # FoodUpload 객체들 가져오기
        food_uploads = FoodUpload.objects.filter(id__in=food_upload_ids, user=request.user)

        if not food_uploads.exists():
            return Response({"error": "음식 업로드 기록이 없습니다."}, status=400)

        # DailyNutrition에서 해당 날짜의 기록 가져오기
        daily_nutrition = DailyNutrition.objects.filter(user=request.user, date=date.today()).first()

        if not daily_nutrition:
            return Response({"error": "영양성분 기록이 없습니다."}, status=400)

        # 사용자 목표 영양성분 가져오기
        user_goal = request.user.usergoal

        # 목표와 섭취량 차이 계산
        calorie_diff = round(daily_nutrition.calories - user_goal.daily_calories, 1)
        protein_diff = round(daily_nutrition.protein - user_goal.protein_goal, 1)
        fat_diff = round(daily_nutrition.fat - user_goal.fat_goal, 1)
        carbs_diff = round(daily_nutrition.carbs - user_goal.carbs_goal, 1)

        # 목표와 섭취량 차이에 따른 성공/실패 여부 결정
        within_range = (
            abs(calorie_diff) <= 100 and
            abs(protein_diff) <= 10 and
            abs(fat_diff) <= 10 and
            abs(carbs_diff) <= 10
        )

        result = "성공했습니다!" if within_range else "실패했습니다!"

        # 게시글 생성
        post = Post.objects.create(
            user=request.user,
            title=title,  # 제목 추가
            total_calories=daily_nutrition.calories,
            total_protein=daily_nutrition.protein,
            total_fat=daily_nutrition.fat,
            total_carbs=daily_nutrition.carbs,
            goal_calories=request.user.usergoal.daily_calories,
            goal_protein=request.user.usergoal.protein_goal,
            goal_fat=request.user.usergoal.fat_goal,
            goal_carbs=request.user.usergoal.carbs_goal,
            result=result,
            caption=caption
        )

        # 선택한 음식 업로드들 연결
        post.food_uploads.set(food_uploads)
        post.save()


        return Response({"message": "게시글이 성공적으로 업로드되었습니다.", "id": post.id}, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like
from .serializers import PostDetailSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated


class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request, post_id, *args, **kwargs):
        # 게시글을 ID로 가져오기
        post = get_object_or_404(Post, id=post_id)

        # 게시글 데이터 직렬화
        serializer = PostDetailSerializer(post)
        
        # 직렬화된 데이터를 응답으로 반환
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, pk=post_id)  # 댓글을 달기 위해 게시글을 가져옴
        serializer = CommentSerializer(data=request.data, context={'request': request})  # request context 전달
        if serializer.is_valid():
            serializer.save(post=post)  # 게시글과 함께 댓글 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, post_id, *args, **kwargs):
        # 게시글 가져오기 (좋아요 추가)
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)  # 좋아요 추가

        # 좋아요를 처음 누른 경우
        if created:
            return Response({"message": "좋아요를 눌렀습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, *args, **kwargs):
        # 게시글 가져오기 (좋아요 삭제)
        post = get_object_or_404(Post, id=post_id)
        try:
            like = Like.objects.get(user=request.user, post=post)  # 해당 유저의 좋아요 가져오기
            like.delete()  # 좋아요 삭제
            return Response({"message": "좋아요가 해제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({"message": "먼저 좋아요를 눌러주세요."}, status=status.HTTP_400_BAD_REQUEST)





