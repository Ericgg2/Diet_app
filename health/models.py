from django.contrib.auth.models import User
from django.db import models
from datetime import date

class FoodUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='food_images/')  # 이미지 업로드 필드
    weight = models.FloatField()  # 사용자가 입력한 음식의 무게 (그램)
    predicted_food = models.CharField(max_length=100, blank=True, null=True)  # 딥러닝 모델이 예측한 음식
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 업로드 날짜 기록

class DailyUploadCount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 사용자마다 한 개의 카운트만 가짐
    date = models.DateField(default=date.today)  # 마지막으로 업로드한 날짜
    count = models.IntegerField(default=0)  # 당일 업로드 카운트
