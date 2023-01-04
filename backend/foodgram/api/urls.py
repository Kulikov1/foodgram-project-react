from django.urls import include, path
from rest_framework.routers import SimpleRouter

from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    IngredientAmountViewSet)

app_name = 'api'

router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tag', TagViewSet)
router.register('IngredientAmount', IngredientAmountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
