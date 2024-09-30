from django.contrib.auth.models import User
from django.db import models
from datetime import date

class FoodUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='food_images/')  # 이미지 업로드 필드
    weight = models.FloatField()  # 사용자가 입력한 음식의 무게 (그램)
    predicted_food = models.CharField(max_length=100, blank=True, null=True)  # 딥러닝 모델이 예측한 음식
    calories = models.FloatField(null=True, blank=True)  # 영양성분: 칼로리
    protein = models.FloatField(null=True, blank=True)  # 영양성분: 단백질
    fat = models.FloatField(null=True, blank=True)  # 영양성분: 지방
    carbs = models.FloatField(null=True, blank=True)  # 영양성분: 탄수화물
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 업로드 날짜 기록
    last_meal = models.BooleanField(default=False)  # 마지막 끼니 여부 추가


class DailyUploadCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 사용자마다 한 개의 카운트만 가짐
    date = models.DateField(default=date.today)  # 마지막으로 업로드한 날짜
    count = models.IntegerField(default=0)  # 당일 업로드 카운트

class DailyNutrition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    calories = models.FloatField(default=0.0)
    protein = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)

    def reset_daily_values(self):
        """하루 영양성분 리셋"""
        self.calories = 0.0
        self.protein = 0.0
        self.fat = 0.0
        self.carbs = 0.0

    def update_nutrition(self, calories, protein, fat, carbs):
        """영양성분 업데이트"""
        self.calories += calories
        self.protein += protein
        self.fat += fat
        self.carbs += carbs

    def __str__(self):
        return f"{self.user.username}'s nutrition for {self.date}"
