from rest_framework import viewsets, serializers
from rest_framework.pagination import PageNumberPagination
from .models import Ingredient, Recipe, IngredientAmount, Tag

from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeCreateSerializer,
    TagSerializer,
    IngredientAmountSerializer
)


class IngredientAmountViewSet(viewsets.ModelViewSet):
    ingredients = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Ingredient.objects.all(),
        many=True)
    queryset = IngredientAmount.objects.all()
    serializer_class = IngredientAmountSerializer
    pagination_class = PageNumberPagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение и создание рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer
