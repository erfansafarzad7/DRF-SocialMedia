from rest_framework import generics, viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, OTPVerification, Follow, Notification
from .serializers import (OTPRequestSerializer, OTPVerifySerializer, PasswordResetRequestSerializer,
                          PasswordResetConfirmSerializer, FollowSerializer, NotificationSerializer)


class OTPRequestView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):

    def create_token_response(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(self.create_token_response(user))


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobile']

        try:
            user = CustomUser.objects.get(mobile=mobile)
            otp = user.generate_otp()
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not otp:
            return Response({"message": "Please wait before requesting another OTP."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({"message": "OTP sent to mobile."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."})


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        followers = user.followers.all()
        following = user.following.all()
        return Response({
            "followers": [f.follower.username for f in followers],
            "following": [f.following.username for f in following]
        })

    def create(self, request):
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        following = serializer.validated_data.get("following")
        user = self.request.user

        # Prevent a user from following themselves
        if user == following:
            raise ValidationError({"message": "You cannot follow yourself."})

        # Prevent duplicate follows
        if following.id in user.following.values_list('following', flat=True):
            raise ValidationError({"message": "You are already following this user."})

        serializer.save(follower=self.request.user)
        return Response(serializer.data, status=201)


class NotificationView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)

