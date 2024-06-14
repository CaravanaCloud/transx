from django.db import models # type: ignore #ignore type
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin # type: ignore #ignore type
from django.contrib.auth.models import BaseUserManager as BUM # type: ignore #ignore type
from django.db import models # type: ignore #ignore type
from django.utils import timezone # type: ignore #ignore type
import uuid # type: ignore #ignore type

# Create your models here.

# class BaseModel(models.Model):
#     created_at = models.DateTimeField(db_index=True, default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True


class BaseUserManager(BUM):
    def create_user(self, email, is_active=True, is_admin=False, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email.lower()),
            is_active=is_active,
            is_admin=is_admin,
        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            is_active=True,
            is_admin=True,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user


class BaseUser(AbstractBaseUser):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # This should potentially be an encrypted field
    jwt_key = models.UUIDField(default=uuid.uuid4)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def is_staff(self):
        return self.is_admin