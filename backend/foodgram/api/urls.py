from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    IngredientViewSet,
    RecipesViewSet,
    TagViewSet,
    IngredientAmountViewSet)

app_name = 'api'

router = SimpleRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipesViewSet)
router.register('tag', TagViewSet)
router.register('IngredientAmount', IngredientAmountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
