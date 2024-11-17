from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from utils.validators import phone_regex
from .managers import CustomUserManager
from datetime import timedelta
from random import randint
import time


def generate_random_username():
    return f"User_{int(time.time()) + randint(1, 9999)}"


class OTPVerification(models.Model):
    mobile = models.CharField(_('Mobile Number'), max_length=11, validators=[phone_regex], unique=True)
    code = models.CharField(_('One Time Password'), max_length=6, default=randint(100000, 999999))
    created_at = models.DateTimeField(_('OTP Create Time'), null=True, blank=True)

    def __str__(self):
        return f"OTP for {self.mobile}"

    def send_with_sms(self):
        """
        Sends the OTP code via SMS to the user's mobile number.
        """
        print(f'OTP Code: {self.code} - To: {self.mobile}')

    def valid_delay(self):
        """
        Checks if at least 3 minutes have passed since the last OTP generation.
        """
        if self.created_at and now() <= self.created_at + timedelta(minutes=3):
            return False

        self.created_at = now()
        self.save()
        return True

    def is_otp_valid(self, otp):
        """
        Verifies if the provided OTP matches the generated code and
        ensures it has not expired (valid for up to 5 minutes).
        """
        if self.code == str(otp) and now() <= self.created_at + timedelta(minutes=5):
            return True
        return False


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('Username'), max_length=30, default=generate_random_username, unique=True)
    mobile = models.CharField(_('Mobile Number'), max_length=11, validators=[phone_regex, ], unique=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    is_staff = models.BooleanField(_('Is Staff'), default=False)
    created_at = models.DateField(_('Created At'), auto_now_add=True)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    def generate_otp(self):
        otp, create = OTPVerification.objects.get_or_create(mobile=self.mobile)
        if otp.valid_delay():
            otp.send_with_sms()
            return True
        return


class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(_('Is Read'), default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
