from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint
from django.forms import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    slug = models.SlugField(max_length=20)

    class Meta:
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='Recipe'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipe',
        verbose_name='автор')
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        related_name='Recipe',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='Количество',
        on_delete=models.CASCADE
    )
    recipes = models.ForeignKey(
        Recipe,
        related_name='Количество',
        on_delete=models.CASCADE
    )
    amount = models.FloatField(
        validators=[MinValueValidator(0.1, message='Должно быть > 0'), ]
    )

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
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            )
        ]
    
    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Подписка на самого себя запрещена!'
            )

    def __str__(self):
        return (f'Подписка {self.user.get_username}',
                f'на: {self.author.get_username}')
