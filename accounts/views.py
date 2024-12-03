from rest_framework import generics, viewsets, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from utils import custom_permissions
from .models import OTPVerification, CustomUser, Notification
from .serializers import (UserListSerializer, UserDetailSerializer, OTPRequestSerializer, OTPVerifySerializer,
                          PasswordResetConfirmSerializer, FollowSerializer,
                          ChangeMobileConfirmSerializer, NotificationSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    View to list, retrieve and update users.
    Create and Delete are not allowed.
    """

    queryset = CustomUser.objects.all().order_by('-created_at')
    permission_classes = [custom_permissions.IsOwnProfile]  # Users only can edit their own profile
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]  # Fields available for searching
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    def get_serializer_class(self):
        """
        Choose serializer for (list/retrieve).
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class OTPRequestView(APIView):
    """
    View to send an OTP to the user's mobile number.
    """

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    """
    View to verify OTP and authenticate user.
    If OTP is valid, generate and return JWT tokens (refresh and access).
    """

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


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    A view to handle the password reset confirmation.
    """

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the new password after successful validation
        serializer.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


class ChangeMobileConfirmView(generics.GenericAPIView):
    """
    API View for confirming and updating the mobile number of an authenticated user.
    """

    serializer_class = ChangeMobileConfirmSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the new mobile after successful validation
        serializer.save()
        return Response({"message": "Mobile has been changed successfully."}, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FollowViewSet(viewsets.ViewSet):
    """
    A ViewSet to manage user follow and unfollow actions.
    Users can view their followers and following lists, and follow/unfollow others.
    """

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Returns the lists of usernames for both followers and following users.
        """
        user = request.user
        followers = user.followers.all()
        following = user.followings.all()
        return Response({
            "followers": [f.follower.username for f in followers],
            "following": [f.following.username for f in following]
        })

    def create(self, request):
        """
        Allows a user to follow another user.
        Ensures the user cannot follow themselves and prevents duplicate follow actions.
        """

        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        following = serializer.validated_data.get("following")
        user = self.request.user

        # Prevent a user from following themselves
        if user == following:
            raise ValidationError({"message": "You cannot follow yourself."})

        # Prevent duplicate follows
        # if following.id in user.following.values_list('following', flat=True):
        if user.following.filter(following=following).first():
            raise ValidationError({"message": "You are already following this user."})

        serializer.save(follower=user)
        return Response(serializer.data, status=201)

    def delete(self, request):
        """
        Allows a user to unfollow another user.
        Ensures that the user can only unfollow someone they are currently following.
        """
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        following = serializer.validated_data.get("following")
        user = self.request.user

        # Check if the user is following the other user
        follow_instance = user.following.filter(following=following).first()

        if not follow_instance:
            raise ValidationError({"message": "You are not following this user."})

        # Remove the follow relationship
        follow_instance.delete()
        return Response({"message": "You have unfollowed this user."}, status=status.HTTP_204_NO_CONTENT)


class NotificationView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)

