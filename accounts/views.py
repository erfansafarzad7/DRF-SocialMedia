from rest_framework import generics, viewsets, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from utils import custom_permissions
from .models import CustomUser, Notification
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    PasswordResetConfirmSerializer,
    FollowSerializer,
    ChangeMobileConfirmSerializer,
    NotificationSerializer
)


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


class ProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [custom_permissions.IsOwnProfile]

    def get_object(self):
        return self.request.user

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

            return Response({
                "message": "OTP sent successfully!"
            }, status=status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class OTPVerifyView(APIView):
    """
    View to verify OTP and authenticate user.
    If OTP is valid, generate and return JWT tokens (refresh and access).
    """

    def create_token_response(self, user):
        """
        Creates JWT tokens (refresh and access) for the authenticated user.
        """
        refresh = RefreshToken.for_user(user)  # Generate the refresh token for the user
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def post(self, request):
        """
        Handles the OTP verification and user authentication.
        """
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Save the user object after successful OTP validation
        return Response(self.create_token_response(user))  # Return the generated JWT tokens


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    A view to handle the password reset confirmation.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the new password after successful validation

        return Response({
            "message": "Password has been reset successfully."
        }, status=status.HTTP_200_OK)


class ChangeMobileConfirmView(generics.GenericAPIView):
    """
    API View for confirming and updating the mobile number of an authenticated user.
    """
    serializer_class = ChangeMobileConfirmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the new mobile after successful validation

        return Response({
            "message": "Mobile has been changed successfully."
        }, status=status.HTTP_200_OK)

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
        followings = user.followings.all()
        return Response({
            "followers": [f.follower.username for f in followers],
            "followings": [f.following.username for f in followings]
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
            raise ValidationError({
                "message": "You cannot follow yourself."
            })

        # Prevent duplicate follows
        if user.followings.filter(following=following).first():
            raise ValidationError({
                "message": "You are already following this user."
            })

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
        follow_instance = user.followings.filter(following=following).first()

        if not follow_instance:
            raise ValidationError({
                "message": "You are not following this user."
            })

        # Remove the follow relationship
        follow_instance.delete()

        return Response({
            "message": "You have unfollowed this user."
        }, status=status.HTTP_204_NO_CONTENT)


class NotificationView(generics.ListAPIView):
    """
    API view to retrieve a list of notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Override the default queryset to filter notifications by the current user.
        """
        user = self.request.user
        return Notification.objects.filter(user=user).first()
