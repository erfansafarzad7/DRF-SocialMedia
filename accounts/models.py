from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from datetime import timedelta
import random


class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created = models.DateTimeField(blank=True, null=True)
    otp_last_sent = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.mobile

    def generate_otp(self):
        current_time = timezone.now()
        if self.otp_last_sent and current_time < self.otp_last_sent + timedelta(minutes=2):
            return None

        self.otp = str(random.randint(100000, 999999))
        self.otp_created = current_time
        self.otp_last_sent = current_time
        self.save()
        return self.otp
