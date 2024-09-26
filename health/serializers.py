from rest_framework import serializers
from .models import FoodUpload

class FoodUploadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # 사용자 이름만 출력
    last_meal = serializers.BooleanField(write_only=True, required=False)  # 직렬화 과정에서만 사용

    class Meta:
        model = FoodUpload
        fields = ['user', 'image', 'weight', 'predicted_food', 'uploaded_at', 'last_meal']
    
    def create(self, validated_data):
        # 'last_meal' 필드를 validated_data에서 제거하여 FoodUpload 모델에 전달되지 않도록 합니다.
        validated_data.pop('last_meal', None)  # 'last_meal'은 저장하지 않음

        return FoodUpload.objects.create(**validated_data)
