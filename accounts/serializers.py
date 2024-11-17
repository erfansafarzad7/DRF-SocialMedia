from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from utils.validators import phone_regex
from .models import CustomUser, OTPVerification, Follow, Notification
from random import randint


User = get_user_model()


class OTPVerificationBaseSerializer(serializers.Serializer):
    """
    A base serializer for handling OTP verification and password reset confirmation.
    Validates the mobile number and OTP, ensuring the OTP is valid and not expired.
    """

    mobile = serializers.CharField(max_length=11, validators=[phone_regex])
    otp = serializers.CharField(max_length=6)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.otp_verification = None  # Initialize OTP verification instance

    def validate(self, data):
        otp = data.get('otp')
        mobile = data.get('mobile')

        try:
            otp_verification = OTPVerification.objects.get(mobile=mobile)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({'mobile': 'Invalid Mobile Number Or OTP.'})

        # Check if the provided OTP is valid and has not expired
        if not otp_verification.is_otp_valid(otp) or not otp.isdigit():
            raise serializers.ValidationError({'otp': 'Invalid or expired OTP.'})

        self.otp_verification = otp_verification  # Initialize OTP verification instance
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
            raise serializers.ValidationError({'message': 'Wait Until Delay Ends.'})

        return otp


class OTPVerifySerializer(OTPVerificationBaseSerializer):
    """
    Create or return an exist user after verification has been done.
    """

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            mobile=validated_data['mobile']
        )
        self.otp_verification.delete()  # Remove the used OTP instance
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, validators=[phone_regex])


class PasswordResetConfirmSerializer(OTPVerificationBaseSerializer):
    """
    Serializer for confirming password reset.
    Inherits from OTPVerificationBaseSerializer and adds a new password field.
    """

    new_password = serializers.CharField()

    def validate(self, data):
        data = super().validate(data)  # Validate OTP and mobile

        # Validate the entered password
        password_validation.validate_password(data['new_password'])
        return data

    def save(self):
        """
        Saves the new password for the user.
        """

        user = CustomUser.objects.get(mobile=self.validated_data['mobile'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        self.otp_verification.delete()  # Remove the used OTP instance
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
