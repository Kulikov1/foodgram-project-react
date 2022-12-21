from django.db import models
from users.models import User


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


class Recipes(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='Recipes'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='автор')
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        related_name='Recipes',
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
        Recipes,
        related_name='Количество',
        on_delete=models.CASCADE
    )
    amount = models.PositiveBigIntegerField()
