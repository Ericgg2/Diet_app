from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FoodUpload, DailyUploadCount, DailyNutrition
from users.models import UserProfile, UserGoal
from .serializers import FoodUploadSerializer
from  diet_app.food_model import predict_food  # 딥러닝 예측 함수
import os
from datetime import date
from .nutrition_get import get_nutritional_info
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated


class FoodUploadView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request, *args, **kwargs):
        # 요청한 사용자 정보 가져오기
        user = request.user

        # 사용자의 DailyUploadCount 가져오기, 없으면 생성
        daily_upload, created = DailyUploadCount.objects.get_or_create(user=user)

        # 오늘 날짜와 다르면 카운트 초기화
        if daily_upload.date != date.today():
            daily_upload.date = date.today()
            daily_upload.count = 0

        # 카운트 증가
        daily_upload.count += 1
        daily_upload.save()

        serializer = FoodUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 이미지 파일 저장 (사용자 정보 포함)
            food_upload = serializer.save(user=user)

            # 이미지 경로 가져오기
            image_path = food_upload.image.path

            # 딥러닝 모델을 사용해 예측
            predicted_food = predict_food(image_path)

            # 예측된 음식 이름을 인스턴스에 저장
            food_upload.predicted_food = predicted_food
            food_upload.save()

            # 영양성분 정보 가져오기
            weight = food_upload.weight
            nutrition_info = get_nutritional_info(predicted_food, weight)

            # 영양성분 저장
            calories = nutrition_info.get('calories', 0)
            protein = nutrition_info.get('protein', 0)
            fat = nutrition_info.get('fat', 0)
            carbs = nutrition_info.get('carbs', 0)

            # 오늘 날짜의 DailyNutrition 가져오기 또는 생성하기
            daily_nutrition, created = DailyNutrition.objects.get_or_create(
                user=user, date=date.today(),
                defaults={'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            )

            # 영양성분을 누적
            daily_nutrition.calories += calories
            daily_nutrition.protein += protein
            daily_nutrition.fat += fat
            daily_nutrition.carbs += carbs
            daily_nutrition.save()

            # 목표 영양성분 가져오기
            user_profile = UserProfile.objects.get(user=user)
            user_goal = UserGoal.objects.get(user=user)

            # 목표 영양성분 비교
            calorie_diff = daily_nutrition.calories - user_goal.daily_calories
            protein_diff = daily_nutrition.protein - user_goal.protein_goal
            fat_diff = daily_nutrition.fat - user_goal.fat_goal
            carbs_diff = daily_nutrition.carbs - user_goal.carbs_goal

            # 오차 범위 계산 (칼로리 ±100, 영양소 ±10)
            within_range = (
                abs(calorie_diff) <= 100 and
                abs(protein_diff) <= 10 and
                abs(fat_diff) <= 10 and
                abs(carbs_diff) <= 10
            )

            # 마지막 끼니인지 여부 확인
            last_meal = request.data.get('last_meal', False)

            if last_meal:
                if within_range:
                    message = f"오늘의 목표 달성! 성공했습니다! 총 섭취량: {daily_nutrition.calories}kcal."
                else:
                    message = f"오늘의 목표 실패! 총 섭취량: {daily_nutrition.calories}kcal, 목표와의 차이: {calorie_diff}kcal."
            else:
                # 마지막 끼니가 아니어도 영양성분의 차이를 알려줌
                if calorie_diff < -100:
                    message = f"{daily_upload.count}번째 음식이 성공적으로 업로드되었습니다. 칼로리가 {abs(calorie_diff)}kcal 부족합니다. 더 드셔야 해요!"
                elif calorie_diff > 100:
                    message = f"{daily_upload.count}번째 음식이 성공적으로 업로드되었습니다. 칼로리가 {calorie_diff}kcal 초과했습니다. 그만 드셔야 해요!"
                else:
                    message = f"{daily_upload.count}번째 음식이 성공적으로 업로드되었습니다. 칼로리가 적당합니다!"

            return Response({
                'message': message,
                'predicted_food': predicted_food,
                'total_calories': daily_nutrition.calories,
                'total_protein': daily_nutrition.protein,
                'total_fat': daily_nutrition.fat,
                'total_carbs': daily_nutrition.carbs,
                'calorie_diff': calorie_diff,
                'protein_diff': protein_diff,
                'fat_diff': fat_diff,
                'carbs_diff': carbs_diff
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
