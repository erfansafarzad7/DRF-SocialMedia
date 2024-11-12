from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from datetime import timedelta
import random


def generate_random_username():
    random_number = random.randint(10000, 99999)
    return f"User_{random_number}"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(_('Mobile Number'), max_length=15, unique=True)
    username = models.CharField(_('Username'), max_length=30, default=generate_random_username, unique=True)
    otp = models.CharField(_('One Time Password'), max_length=6, blank=True, null=True)
    otp_created = models.DateTimeField(_('OTP Created Time'), blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    is_staff = models.BooleanField(_('Is Staff'), default=False)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def generate_otp(self):
        current_time = timezone.now()
        if self.otp_created and current_time < self.otp_created + timedelta(minutes=2):
            return None

        self.otp = str(random.randint(100000, 999999))
        self.otp_created = current_time
        self.save()
        return self.otp


class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"
