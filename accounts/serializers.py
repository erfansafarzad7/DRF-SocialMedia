from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, Follow
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['mobile']


class UserOTPLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(mobile=data['mobile'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp != data['otp'] or timezone.now() > user.otp_created + timedelta(minutes=5):
            raise serializers.ValidationError("Invalid or expired OTP.")

        return data


class UserPasswordLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(mobile=data['mobile'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        return data


class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField()

    def validate(self, data):
        if not CustomUser.objects.filter(mobile=data['mobile']).exists():
            raise serializers.ValidationError("User not found.")
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField()

    def validate(self, data):
        if not CustomUser.objects.filter(mobile=data['mobile']).exists():
            raise serializers.ValidationError("User not found.")
        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    otp = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(mobile=data['mobile'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # بررسی صحت OTP
        if user.otp != data['otp'] or timezone.now() > user.otp_created + timedelta(minutes=5):
            raise serializers.ValidationError("Invalid or expired OTP.")

        password_validation.validate_password(data['new_password'], user)
        return data

    def save(self):
        user = CustomUser.objects.get(mobile=self.validated_data['mobile'])
        user.set_password(self.validated_data['new_password'])
        user.otp = None  # حذف OTP پس از استفاده
        user.save()
        return user


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.ReadOnlyField(source='follower.username')
    following = serializers.SlugRelatedField(slug_field="username", queryset=CustomUser.objects.all())

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']
