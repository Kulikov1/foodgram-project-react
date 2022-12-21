from rest_framework import viewsets, serializers
from rest_framework.pagination import PageNumberPagination
from recipes.models import Ingredient, Recipes, IngredientAmount, Tag

from .serializers import (
    IngredientSerializer,
    RecipesSerializer,
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


class RecipesViewSet(viewsets.ModelViewSet):
    ingredients = serializers.SlugRelatedField(
        slug_field='id',
        queryset=IngredientAmount.objects.all(),
        many=True)
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
