from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, UserGoal

class SignUpSerializer(serializers.ModelSerializer):
    height = serializers.FloatField(required=True)
    weight = serializers.FloatField(required=True)
    age = serializers.IntegerField(required=True)
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=True)
    activity_level = serializers.ChoiceField(choices=[
        ('sedentary', '좌식'),
        ('light', '가벼운 활동'),
        ('moderate', '적당한 활동'),
        ('very_active', '매우 활동적'),
        ('extra_active', '매우 활동적인 경우')
    ], required=True)
    goal_type = serializers.ChoiceField(choices=[
        ('diet', '다이어트'),
        ('maintain', '유지'),
        ('bulk', '벌크업')
    ], required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'height', 'weight', 'age', 'gender', 'activity_level', 'goal_type']

    def create(self, validated_data):
        # 사용자 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # 입력한 정보로 BMR 계산
        height = validated_data['height']
        weight = validated_data['weight']
        age = validated_data['age']
        gender = validated_data['gender']
        activity_level = validated_data['activity_level']
        goal_type = validated_data['goal_type']

        # BMR 계산
        if gender == 'M':
            bmr = 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age)
        else:
            bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

        # 활동 수준에 따른 총 칼로리 계산
        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        total_calories = bmr * activity_factors[activity_level]


        # 목표에 따른 총 칼로리 조정 (다이어트는 -500, 벌크업은 +500)
        if goal_type == 'diet':
            total_calories -= 500
        elif goal_type == 'bulk':
            total_calories += 500

        # 대략적인 영양소 목표 설정, 소수점 1자리까지만 나오도록 round 적용
        protein_goal = round((total_calories * 0.3) / 4, 1)  # 단백질: 1g당 4kcal
        fat_goal = round((total_calories * 0.25) / 9, 1)     # 지방: 1g당 9kcal
        carbs_goal = round((total_calories * 0.45) / 4, 1)   # 탄수화물: 1g당 4kcal
        total_calories = round(total_calories, 1)            # 총 칼로리 소수점 1자리까지
        # UserProfile 생성
        UserProfile.objects.create(
            user=user,
            height=height,
            weight=weight,
            age=age,
            gender=gender,
            activity_level=activity_level,
            bmr = bmr
        )

        UserGoal.objects.create(
            user=user,
            goal_type=goal_type,
            daily_calories=total_calories,
            protein_goal=protein_goal,
            fat_goal=fat_goal,
            carbs_goal=carbs_goal,
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("로그인 정보가 잘못되었습니다.")


class GoalSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGoal
        fields = ['goal_type', 'daily_calories', 'protein_goal', 'fat_goal', 'carbs_goal']


class ProfileSerializer(serializers.ModelSerializer):
    goal = serializers.SerializerMethodField()  # 추가
    username = serializers.CharField(source='user.username')  # user 모델의 username 필드 추가

    class Meta:
        model = UserProfile
        fields = ['username', 'height', 'weight', 'age', 'gender', 'bmr', 'activity_level', 'goal']

    def get_goal(self, obj):
        try:
            goal = UserGoal.objects.get(user=obj.user)
            return GoalSerializer(goal).data  # goal을 직렬화하여 반환
        except UserGoal.DoesNotExist:
            return None  # 목표가 없을 경우 None 반환