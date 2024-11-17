from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from utils.validators import phone_regex
from .models import CustomUser, OTPVerification, Follow, Notification
from random import randint


User = get_user_model()


class OTPVerificationBaseSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, validators=[phone_regex])
    otp = serializers.CharField(max_length=6)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.otp_verification = None

    def validate(self, data):
        otp = data.get('otp')
        mobile = data.get('mobile')

        try:
            otp_verification = OTPVerification.objects.get(mobile=mobile)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({'mobile': 'Invalid Mobile Number Or OTP.'})

        if not otp_verification.is_otp_valid(otp) or not otp.isdigit():
            raise serializers.ValidationError({'otp': 'Invalid or expired OTP.'})

        self.otp_verification = otp_verification
        return data


class OTPRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, validators=[phone_regex])

    def create(self, validated_data):
        otp, created = OTPVerification.objects.get_or_create(mobile=validated_data['mobile'])

        if otp.valid_delay():
            otp.code = randint(100000, 999999)
            otp.save()
            otp.send_with_sms()
        else:
            raise serializers.ValidationError('Wait Until Delay Ends.')

        return otp


class OTPVerifySerializer(OTPVerificationBaseSerializer):
    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            mobile=validated_data['mobile']
        )
        self.otp_verification.delete()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, validators=[phone_regex])


class PasswordResetConfirmSerializer(OTPVerificationBaseSerializer):
    new_password = serializers.CharField()

    def validate(self, data):
        data = super().validate(data)

        password_validation.validate_password(data['new_password'])
        return data

    def save(self):
        user = CustomUser.objects.get(mobile=self.validated_data['mobile'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        self.otp_verification.delete()
        return user


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.ReadOnlyField(source='follower.username')
    following = serializers.SlugRelatedField(slug_field="username", queryset=CustomUser.objects.all())

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']
