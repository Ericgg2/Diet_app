from rest_framework import serializers
from .models import FoodUpload

class FoodUploadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # 사용자 이름만 출력

    class Meta:
        model = FoodUpload
        fields = ['user', 'image', 'weight', 'predicted_food', 'uploaded_at']
