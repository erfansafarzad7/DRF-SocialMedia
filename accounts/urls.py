from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (
    OTPRequestView,
    OTPVerifyView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    FollowViewSet,
    NotificationView
)

follow_list = FollowViewSet.as_view({'get': 'list'})
follow = FollowViewSet.as_view({'post': 'create'})
unfollow = FollowViewSet.as_view({'delete': 'delete'})

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('otp-request/', OTPRequestView.as_view(), name='otp_request'),
    path('otp-verify/', OTPVerifyView.as_view(), name='otp_verify'),

    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('follow-list/', follow_list, name='follow-list'),
    path('follow/', follow, name='follow'),
    path('unfollow/', unfollow, name='unfollow'),

    path('notifications/', NotificationView.as_view(), name='notifications'),
]
