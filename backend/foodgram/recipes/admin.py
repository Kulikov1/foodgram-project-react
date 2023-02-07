from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    IngredientAmount,
    ShoppingCart,
    Tag
)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1



@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('name', 'author__email', 'tags')
    inlines = [
        IngredientAmountInline
    ]

    @admin.display(description='В избранном')
    def count_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientAmount)
class RecipeIngredientCartAdmin(admin.ModelAdmin):
    pass
