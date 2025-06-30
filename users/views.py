from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from .serializers import CustomTokenObtainPairSerializer
from users.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_by_admin(request):
    if request.user.role != 'admin':
        return Response({"error": "Unauthorized. Only admin can create users."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    required_fields = ['email', 'username', 'first_name', 'last_name', 'password', 'role']

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return Response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

    if data['role'] not in ['student', 'teacher']:
        return Response({"error": "Invalid role. Use 'student' or 'teacher'."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data['email']).exists():
        return Response({"error": "User with this email already exists."}, status=status.HTTP_409_CONFLICT)

    if User.objects.filter(username=data['username']).exists():
        return Response({"error": "Username already taken."}, status=status.HTTP_409_CONFLICT)

    user = User.objects.create(
        email=data['email'],
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password=make_password(data['password']),
        role=data['role']
    )

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "first_name": user.first_name,
        "last_name": user.last_name
    }, status=status.HTTP_201_CREATED)

# Create your views here.
class CustomTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView1(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView0(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
