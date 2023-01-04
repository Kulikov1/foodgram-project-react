from django.contrib import admin

from recipes.models import (Tag, Ingredient, Recipe, IngredientAmount)
                    #  Favorite, ShoppingCart Follow


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientInline,)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount',
    )
    empty_value_display = '-пусто-'


# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'recipe',
#     )
#     empty_value_display = '-пусто-'


# class ShoppingCartAdmin(admin.ModelAdmin):
#     list_display = (
#         'user',
#         'recipe',
#     )
#     empty_value_display = '-пусто-'


# admin.site.register(Follow, FollowAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(IngredientAmount, IngredientToRecipeAdmin)
# admin.site.register(Favorite, FavoriteAdmin)
# admin.site.register(ShoppingCart, ShoppingCartAdmin)