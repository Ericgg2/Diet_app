from django.db import models
from django.contrib.auth.models import User

# 사용자 프로필 모델
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.FloatField()  # 키 (cm)
    weight = models.FloatField()  # 몸무게 (kg)
    age = models.IntegerField()  # 나이
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])  # 성별
    activity_level = models.CharField(max_length=20, choices=[
        ('sedentary', '좌식'),
        ('light', '가벼운 활동'),
        ('moderate', '적당한 활동'),
        ('very_active', '매우 활동적'),
        ('extra_active', '매우 활동적인 경우')
    ])  # 활동 수준
    bmr = models.FloatField(null=True, blank=True)  # 기초 대사량 (BMR)

    def __str__(self):
        return f"{self.user.username}'s profile"

class UserGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=10, choices=[('Diet', '다이어트'), ('Maintain', '유지'), ('Bulk', '벌크업')])  # 식단 목적
    daily_calories = models.FloatField()  # 하루 목표 칼로리
    protein_goal = models.FloatField()  # 하루 목표 단백질 (g)
    fat_goal = models.FloatField()  # 하루 목표 지방 (g)
    carbs_goal = models.FloatField()  # 하루 목표 탄수화물 (g)
    created_at = models.DateTimeField(auto_now_add=True)  # 목표 설정 날짜
    updated_at = models.DateTimeField(auto_now=True)  # 목표 업데이트 날짜

    def __str__(self):
        return f"{self.user.username}'s goal: {self.goal_type}"
