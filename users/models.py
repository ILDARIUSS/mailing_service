# users/models.py

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserManager(UserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Переопределённый метод для создания суперпользователя.
        """
        if not email:
            raise ValueError("Superuser must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, is_active=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(unique=True)  # Логин через email

    # Дополнительные поля
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'email'  # Логин по email
    REQUIRED_FIELDS = []  # Пароль и email обязательны

    # Устанавливаем кастомный менеджер для пользователя
    objects = UserManager()