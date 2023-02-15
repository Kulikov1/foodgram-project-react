from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        blank=False,
        max_length=254,
        verbose_name='Почта',
        help_text='Введи свою почту!'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    
    class Meta:
        ordering = ('-id',)
        unique_together = ('user', 'author')
    
    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Подписка на самого себя запрещена!'
            )

    def __str__(self):
        return f'{self.user}'