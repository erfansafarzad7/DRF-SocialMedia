from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import (UserRegistrationSerializer, UserOTPLoginSerializer, UserPasswordLoginSerializer,
                          OTPRequestSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.generate_otp()
        return Response({"message": "User registered. OTP sent to mobile."}, status=status.HTTP_201_CREATED)


class BaseUserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get_user(self, validated_data):
        return CustomUser.objects.get(mobile=validated_data['mobile'])

    def create_token_response(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user(serializer.validated_data)
        return Response(self.create_token_response(user))


class UserOTPLoginView(BaseUserLoginView):
    serializer_class = UserOTPLoginSerializer


class UserPasswordLoginView(BaseUserLoginView):
    serializer_class = UserPasswordLoginSerializer


class OTPRequestView(generics.GenericAPIView):
    serializer_class = OTPRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(mobile=serializer.validated_data['mobile'])
        otp = user.generate_otp()
        # Send OTP via SMS or any other service here
        return Response({"message": "OTP sent to mobile."})


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(mobile=serializer.validated_data['mobile'])

        otp = user.generate_otp()
        if otp is None:
            return Response({"message": "Please wait before requesting another OTP."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Send OTP via SMS or any other service here
        return Response({"message": "OTP sent to mobile."})


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."})
