from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель Тегов"""
    name = models.CharField(
        max_length=30,
        verbose_name='Название',
        unique=True
    )
    color = ColorField(default='#FF0000', unique=True)
    slug = models.SlugField(max_length=150, verbose_name='Ссылка', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов"""
    name = models.CharField(
        max_length=150,
        verbose_name='Название ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=30,
        verbose_name='Единица измерения',
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class IngredientAmount(models.Model):
    """Модель связи количества ингредиента и рецепта"""
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredientamount'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во'
    )

    class Meta:
        unique_together = ('ingredient', 'recipe')
        verbose_name = 'Кол-во ингредиентов'
        verbose_name_plural = 'Кол-во ингредиентов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='creator',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
    )
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тэги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    """Модель корзины покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_owner',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
