from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from utils.validators import phone_regex
from .models import CustomUser, OTPVerification, Follow, Notification
from utils.online_user_manager import OnlineUserManager

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users.

    This serializer includes additional fields such as 'is_online' to indicate
    the user's online status and a hyperlink to the user's detail view.
    """
    is_online = serializers.SerializerMethodField()
    user = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='username',
        read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user', 'is_online', 'created_at']

    def get_is_online(self, obj):
        return OnlineUserManager.is_user_online(obj.id)


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailing user and their posts.
    """
    mobile = serializers.SerializerMethodField()
    posts = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='post-detail',
        read_only=True
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'mobile', 'posts', 'created_at']

    def get_mobile(self, obj):
        """
        Show mobile field only if the request user is the object user.
        """
        request = self.context.get('request')
        if request and request.user == obj:
            return obj.mobile
        return None  # Hide the mobile field for other users


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

        # Find OTP object
        try:
            otp_verification = OTPVerification.objects.get(mobile=mobile)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({
                'mobile': 'Invalid Mobile Number Or OTP.'
            })

        # Check if the provided OTP is valid and has not expired
        if not otp_verification.is_otp_valid(otp) or not otp.isdigit():
            raise serializers.ValidationError({
                'otp': 'Invalid or expired OTP.'
            })

        self.otp_verification = otp_verification  # Initialize OTP verification instance
        return data


class OTPRequestSerializer(serializers.Serializer):
    """
    Serializer for handling OTP requests.

    This serializer validates the mobile number and manages OTP generation,
    ensuring delays are respected before regenerating a new OTP.
    """
    mobile = serializers.CharField(max_length=11, validators=[phone_regex])

    def create(self, validated_data):
        """
        Create or update an OTP for the provided mobile number.
        """
        otp, created = OTPVerification.objects.get_or_create(mobile=validated_data['mobile'])

        # Check if the OTP delay allows regeneration
        if otp.valid_delay():
            otp.regenerate_otp()
            otp.send_with_sms()
        else:
            raise serializers.ValidationError({
                'message': 'Wait Until Delay Ends.'
            })

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


class PasswordResetConfirmSerializer(OTPVerificationBaseSerializer):
    """
    Serializer for confirming password reset.
    Inherits from OTPVerificationBaseSerializer and adds a new password field.
    """
    new_password = serializers.CharField()
    old_password = serializers.CharField()

    def get_user(self):
        """
        Retrieves the user based on the provided mobile number.
        """
        user = CustomUser.objects.filter(
            mobile=self.validated_data['mobile']
        ).first()

        if not user:
            raise serializers.ValidationError({
                "mobile": "User not found."
            })

        return user

    def validate(self, data):
        data = super().validate(data)  # Validate OTP and mobile
        user = self.get_user()  # Use the function to get the user

        # Validate the entered password
        password_validation.validate_password(data['new_password'])

        # Validate old password
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({
                "old_password": "The old password is incorrect."
            })

        return data

    def save(self):
        """
        Saves the new password for the user.
        """
        user = self.get_user()  # Use the function to get the user

        user.set_password(self.validated_data['new_password'])
        user.save()
        self.otp_verification.delete()  # Remove the used OTP instance

        return user


class ChangeMobileConfirmSerializer(OTPVerificationBaseSerializer):
    """
    Serializer for confirming and updating the mobile number of an authenticated user.
    """

    def save(self):
        """
        Saves the new mobile for the user.
        """
        new_mobile = self.validated_data['mobile']
        user = self.context['request'].user

        # Checking not duplicate
        if CustomUser.objects.filter(mobile=new_mobile).first():
            raise serializers.ValidationError({
                'mobile': 'User with this mobile already exists.'
            })

        user.mobile = new_mobile
        user.save()
        self.otp_verification.delete()  # Remove the used OTP instance
        return user


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for managing follow relationships between users.
    """
    follower = serializers.ReadOnlyField(source='follower.username')
    following = serializers.SlugRelatedField(
        slug_field="username",
        queryset=CustomUser.objects.all()  # Ensure the 'following' user exists
    )

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for user notifications.
    """

    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']
