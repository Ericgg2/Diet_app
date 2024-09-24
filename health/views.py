from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FoodUpload, DailyUploadCount
from .serializers import FoodUploadSerializer
from  diet_app.food_model import predict_food  # 딥러닝 예측 함수
import os
from datetime import date

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

        serializer = FoodUploadSerializer(data=request.data)
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

            return Response({
                'message': f'{daily_upload.count}번째 음식이 성공적으로 업로드되었습니다.',
                'predicted_food': predicted_food,
                'weight': food_upload.weight,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
