from rest_framework import serializers
from .models import Post, Comment, Like
from users.models import UserGoal
from .models import Post, FoodUpload
from health.serializers import FoodUploadSerializer
from health.models import FoodUpload


class PostSerializer(serializers.ModelSerializer):
    food_uploads = serializers.PrimaryKeyRelatedField(many=True, queryset=FoodUpload.objects.all())

    class Meta:
        model = Post
        fields = ['food_uploads','title', 'caption']  # 사용자가 입력한 음식 목록과 캡션


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'replies', 'parent_comment']

    def get_replies(self, obj):
        # 해당 댓글의 대댓글을 가져옴
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return None

    def create(self, validated_data):
        # 댓글 작성자의 user를 request.user로 자동 설정
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user', 'post']

class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  # 댓글 포함
    likes_count = serializers.SerializerMethodField()  # 좋아요 수 추가
    food_uploads = FoodUploadSerializer(many=True)  # 여러 음식 업로드 포함
    user = serializers.CharField(source='user.username')  # user의 username을 반환

    class Meta:
        model = Post
        fields = [
            'id','user', 'food_uploads', 'title' ,'total_calories', 'total_protein', 'total_fat', 
            'total_carbs', 'goal_calories', 'goal_protein', 'goal_fat', 'goal_carbs', 
            'result', 'caption', 'created_at', 'comments', 'likes_count'
        ]

    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()

    # comments = CommentSerializer(many=True)
    # remaining_calories = serializers.SerializerMethodField()
    # feedback = serializers.SerializerMethodField()
    # likes_count = serializers.SerializerMethodField()  # 좋아요 수 추가
    # user_liked = serializers.SerializerMethodField()  # 현재 유저의 좋아요 상태 추가

    # class Meta:
    #     model = Post
    #     fields = ['image', 'grams', 'comments', 'remaining_calories', 'feedback', 'likes_count', 'user_liked']

    
    # def get_likes_count(self, obj):
    #     return Like.objects.filter(post=obj).count()  # 해당 게시물의 좋아요 수 반환

    # def get_user_liked(self, obj):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         return Like.objects.filter(post=obj, user=request.user).exists()  # 현재 유저가 좋아요를 눌렀는지 확인
    #     return False  # 비회원일 경우 False 반환

    # def calculate_calories(self, grams):
    #     # Simple logic for calculating calories
    #     return grams  # Example: 2 calories per gram

    # def get_remaining_calories(self, obj):
    #     try:
    #         user_goal = UserGoal.objects.get(user=obj.user)
    #     except UserGoal.DoesNotExist:
    #         return "목표를 먼저 입력해주세요."  # 메시지 반환

    #     calories = self.calculate_calories(obj.grams)
    #     return user_goal.daily_calories - calories

    # def get_feedback(self, obj):
    #     # Logic for feedback based on user nutrition goals
    #     return "feedback"  # Placeholder feedback


