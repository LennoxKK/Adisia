from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import (
    AdvertiserRegistrationSerializer,  # Assuming this serializer exists
    ContentCreatorRegistrationSerializer,  # Assuming this serializer exists
    UserLoginSerializer,
    UserListSerializer,
)
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

User = get_user_model()

class AdvertiserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AdvertiserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({"message": "Advertiser registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentCreatorRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ContentCreatorRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({"message": "Content Creator registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerializer  # Specify the serializer class

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the data

        user = serializer.validated_data['user']  # Retrieve the authenticated user
        login(request, user)  # Log the user in

        return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)


class LogoutSerializer(serializers.Serializer):
    pass  # No fields are needed for logout

class UserLogout(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LogoutSerializer  # Assign a dummy serializer

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication to access this endpoint
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.all()  # Return all users
