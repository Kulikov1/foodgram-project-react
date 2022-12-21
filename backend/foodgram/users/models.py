from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]
    role = models.CharField(
        max_length=20,
        verbose_name='Роль',
        help_text='Роль пользователя',
        choices=ROLE_CHOICES,
        default=USER,
    )
    bio = models.TextField(
        verbose_name='Биография',
        help_text='Расскажите о себе',
        blank=True,
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self) -> str:
        return self.username
