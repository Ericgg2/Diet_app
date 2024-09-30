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

            # 영양성분 정보 가져오기
            weight = food_upload.weight
            nutrition_info = get_nutritional_info(predicted_food, weight)
            
            if nutrition_info:
                # 영양성분 저장
                food_upload.calories = nutrition_info.get('calories', 0)
                food_upload.protein = nutrition_info.get('protein', 0)
                food_upload.fat = nutrition_info.get('fat', 0)
                food_upload.carbs = nutrition_info.get('carbs', 0)
                food_upload.save()
            else:
                # 영양성분을 가져올 수 없는 경우
                food_upload.calories = 0
                food_upload.protein = 0
                food_upload.fat = 0
                food_upload.carbs = 0
                food_upload.save()

            # 오늘 날짜의 DailyNutrition 가져오기 또는 생성하기
            daily_nutrition, created = DailyNutrition.objects.get_or_create(
                user=user, date=date.today(),
                defaults={'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
            )


            # 영양성분을 누적
            daily_nutrition.calories += food_upload.calories
            daily_nutrition.protein += food_upload.protein
            daily_nutrition.fat += food_upload.fat
            daily_nutrition.carbs += food_upload.carbs
            daily_nutrition.save()

            # 목표 영양성분 가져오기
            user_profile = UserProfile.objects.get(user=user)
            user_goal = UserGoal.objects.get(user=user)

            # 목표 영양성분 비교
            calorie_diff = round(daily_nutrition.calories - user_goal.daily_calories, 1)
            protein_diff = round(daily_nutrition.protein - user_goal.protein_goal, 1)
            fat_diff = round(daily_nutrition.fat - user_goal.fat_goal, 1)
            carbs_diff = round(daily_nutrition.carbs - user_goal.carbs_goal, 1)

            # 오차 범위 계산 (칼로리 ±100, 영양소 ±10)
            within_range = (
                abs(calorie_diff) <= 150 and
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
                if calorie_diff < -150:
                    message = f"{daily_upload.count}번째 음식이 성공적으로 업로드되었습니다. 칼로리가 {abs(calorie_diff)}kcal 부족합니다. 더 드셔야 해요!"
                elif calorie_diff > 150:
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
                'carbs_diff': carbs_diff,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.utils.dateparse import parse_date
from datetime import date, timedelta

class DailyFoodView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request):
        # 인증된 사용자의 기록만 조회
        user = request.user


        # 쿼리 파라미터에서 날짜 범위 받아오기 (start_date, end_date)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
        else:
            # 쿼리 파라미터가 없는 경우 기본적으로 최근 3일 내의 기록 조회
            days_before = int(request.query_params.get('days_before', 0))  # 기본적으로 0일 전부터 조회
            start_date = date.today() - timedelta(days=days_before)  # 오늘 기준
            end_date = start_date - timedelta(days=3)  # 3일 전

        # 날짜 형식이 잘못된 경우 에러 처리
        if not start_date or not end_date:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 지정된 기간의 업로드 기록 가져오기
        food_uploads = FoodUpload.objects.filter(
            user=user,
            uploaded_at__date__gte=end_date,
            uploaded_at__date__lte=start_date
        ).order_by('-uploaded_at')

        # 해당 기간의 DailyNutrition 가져오기
        daily_nutritions = DailyNutrition.objects.filter(
            user=user,
            date__gte=end_date,
            date__lte=start_date
        ).order_by('-date')


        # 목표 영양성분 가져오기
        user_profile = UserProfile.objects.get(user=user)
        user_goal = UserGoal.objects.get(user=user)

        # 음식 업로드 기록 직렬화

        # 음식별 영양성분 저장 리스트
        food_nutrition_details = []
        total_nutrition = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

        # 각 음식의 영양성분 추출 (이미 저장된 값 사용)
        for food in food_uploads:
            food_nutrition_details.append({
                'predicted_food': food.predicted_food,
                'weight': food.weight,
                'image_url': food.image.url,
                'calories': food.calories,  # 이미 저장된 값 사용
                'protein': food.protein,    # 이미 저장된 값 사용
                'fat': food.fat,            # 이미 저장된 값 사용
                'carbs': food.carbs,        # 이미 저장된 값 사용
                'uploaded_at': food.uploaded_at
            })

            # 총 영양성분 누적
            if food.calories:
                total_nutrition['calories'] += food.calories
            if food.protein:
                total_nutrition['protein'] += food.protein
            if food.fat:
                total_nutrition['fat'] += food.fat
            if food.carbs:
                total_nutrition['carbs'] += food.carbs

        # 목표 영양성분과의 차이 계산
        calorie_diff = round(total_nutrition['calories'] - user_goal.daily_calories, 1)
        protein_diff = round(total_nutrition['protein'] - user_goal.protein_goal, 1)
        fat_diff = round(total_nutrition['fat'] - user_goal.fat_goal, 1)
        carbs_diff = round(total_nutrition['carbs'] - user_goal.carbs_goal, 1)

        # 각 날짜별로 성공 여부 판단
        nutrition_data = []
        for daily_nutrition in daily_nutritions:
            calorie_diff_daily = round(daily_nutrition.calories - user_goal.daily_calories, 1)
            protein_diff_daily = round(daily_nutrition.protein - user_goal.protein_goal, 1)
            fat_diff_daily = round(daily_nutrition.fat - user_goal.fat_goal, 1)
            carbs_diff_daily = round(daily_nutrition.carbs - user_goal.carbs_goal, 1)

            within_range = (
                abs(calorie_diff_daily) <= 100 and
                abs(protein_diff_daily) <= 10 and
                abs(fat_diff_daily) <= 10 and
                abs(carbs_diff_daily) <= 10
            )

            success_message = "성공했습니다!" if within_range else "실패했습니다!"

            nutrition_data.append({
                'date': daily_nutrition.date,
                'total_calories': round(daily_nutrition.calories, 1),
                'total_protein': round(daily_nutrition.protein, 1),
                'total_fat': round(daily_nutrition.fat, 1),
                'total_carbs': round(daily_nutrition.carbs, 1),
                'calorie_diff': calorie_diff_daily,
                'protein_diff': protein_diff_daily,
                'fat_diff': fat_diff_daily,
                'carbs_diff': carbs_diff_daily,
                'result': success_message  # 날짜별 성공/실패 여부
            })

        return Response({
            'user': user.username,
            'uploads': food_nutrition_details,  # 각 음식의 영양성분 포함
            'daily_nutrition': nutrition_data,
            'total_nutrition': total_nutrition,
            'goal_nutrition': {
                'daily_calories': user_goal.daily_calories,
                'protein_goal': user_goal.protein_goal,
                'fat_goal': user_goal.fat_goal,
                'carbs_goal': user_goal.carbs_goal
            },
            'current_period': f"{start_date} to {end_date}"
        }, status=status.HTTP_200_OK)
