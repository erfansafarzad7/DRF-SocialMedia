from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserOTPLoginView,
    UserPasswordLoginView,
    OTPRequestView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    FollowViewSet
)

router = DefaultRouter()
router.register(r'follows', FollowViewSet)


urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/otp/', UserOTPLoginView.as_view(), name='login_otp'),
    path('login/password/', UserPasswordLoginView.as_view(), name='login_password'),
    path('otp/request/', OTPRequestView.as_view(), name='otp_request'),
    path('password/reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('', include(router.urls)),
]
