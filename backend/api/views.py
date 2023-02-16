import csv

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions, mixins
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated, )
from rest_framework.decorators import action
from .serializers import (
    IngredientSerializer,
    CreateOrUpdateRecipeSerializer,
    ReadOnlyRecipeSerializer,
    TagSerializer,
    FollowSerializer,
    RecipePartInfoSerializer,
    FollowCreateSerializer
)
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    ShoppingCart,
    Favorite,
    IngredientAmount
)
from users.models import Follow

from .pagination import CustomPagination
from .filter import IngredientFilter, TagFilter
from .permissions import AuthorIsRequestUserPermission

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вью для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    filterset_class = IngredientFilter


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вью для отображения одного тега или списка."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """Вью для Рецепта."""

    queryset = Recipe.objects.all()
    serializer_class = CreateOrUpdateRecipeSerializer
    permission_classes = (AuthorIsRequestUserPermission, )
    filterset_class = TagFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadOnlyRecipeSerializer
        return CreateOrUpdateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create_csv_file(self, ingredients):
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; '
                + 'filename="shopping_list.csv"'
            },
            status=status.HTTP_201_CREATED
        )
        ingredients = list(ingredients)

        writer = csv.DictWriter(
            response,
            fieldnames=[
                'ingredient__name',
                'ingredient__measurement_unit',
                'ingredient_total'
            ],
        )
        for row in ingredients:
            writer.writerow(row)
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(Favorite, pk=pk)
        return self.remove_recipe(Favorite, pk=pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, pk=pk)
        return self.remove_recipe(ShoppingCart, pk=pk)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__recipe_in_shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        return self.create_csv_file(ingredients)

    def add_recipe(self, throughmodel, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if throughmodel.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                data={'errors': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        throughmodel.objects.create(recipe=recipe, user=user)
        serializer = RecipePartInfoSerializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def remove_recipe(self, throughmodel, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        instance = throughmodel.objects.filter(
            recipe=recipe,
            user=user
        )
        if not instance.exists():
            return Response(
                data={
                    'errors': 'Нельзя удалить рецепт, '
                    + 'так как он не был добавлен'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListOnlyFollowsAPIView(ListAPIView):
    """Вью для просмотра подписок."""
    serializer_class = FollowCreateSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()


class FollowViewSet(viewsets.ModelViewSet):
    """Вью для подписок."""
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FollowSerializer
        return FollowCreateSerializer

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get('users_id'))
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        return serializer.save(user=self.request.user, author=author)

    def destroy(self, request, users_id):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        instance = Follow.objects.filter(
            author=users_id, user=request.user
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
