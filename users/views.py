from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserProfile, UserGoal
from .serializers import ProfileSerializer, LoginSerializer, GoalSerializer, SignUpSerializer
from django.contrib.auth import login
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def signup_view(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "회원가입이 성공적으로 완료되었습니다.",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileListCreateView(APIView):

    def get(self, request):
        # 모든 프로필 목록 조회
        profiles = UserProfile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)  # 여러 개의 프로필을 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 개별 프로필 조회
        profile = get_object_or_404(UserProfile, user=user)
        
        profile_serializer = ProfileSerializer(profile)

        return Response({
            'profile': profile_serializer.data
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        login(request, user)  # 세션 로그인 처리

        refresh = RefreshToken.for_user(user)

        data = {
            "message": "로그인이 성공적으로 완료되었습니다.",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

        return Response(data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)