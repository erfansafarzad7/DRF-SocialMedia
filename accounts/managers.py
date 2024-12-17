from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model that handles user and superuser creation.
    """

    def create_user(self, mobile, password=None, **extra_fields):
        """
        Create and save a regular user with the given mobile number and password.
        """
        if not mobile:
            raise ValueError("User must have a mobile number.")

        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        """
        Create and save a superuser with the given mobile number and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(mobile, password, **extra_fields)
