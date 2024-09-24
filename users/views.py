from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserProfile, UserGoal
from .serializers import ProfileSerializer, LoginSerializer, GoalSerializer, SignUpSerializer
from django.contrib.auth import login
from django.shortcuts import get_object_or_404


@api_view(['POST'])
def signup_view(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "회원가입이 성공적으로 완료되었습니다."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileListCreateView(APIView):

    def get(self, request):
        # 모든 프로필 목록 조회
        profiles = UserProfile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)  # 여러 개의 프로필을 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileDetailView(APIView):

    def get(self, request, pk):
        # 개별 프로필 조회
        profile = get_object_or_404(UserProfile, pk=pk)
        
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
        return Response({"message": "로그인이 성공적으로 완료되었습니다."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
