from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, permissions, views
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated)
from rest_framework.decorators import action

from .serializers import (IngredientSerializer, CreateOrUpdateRecipeSerializer,
                             ReadOnlyRecipeSerializer, TagSerializer,
                             FollowSerializer)
from recipes.models import Ingredient, Recipe, Tag, ShoppingCart, Favorite
from users.models import Follow
from .pagination import CustomPagination
from .filter import IngredientFilter, TagFilter
from .permissions import IsAuthorOrReadOnly

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс работы с тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class RecipesViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filterset_class = TagFilter
    

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadOnlyRecipeSerializer
        return CreateOrUpdateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(Favorite, pk=pk)
        else:
            return self.remove_recipe(Favorite, pk=pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, pk=pk)
        else:
            return self.remove_recipe(ShoppingCart, pk=pk)


class ListOnlyFollowAPIView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return user.subscribers.all()


class FollowView(views.APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscriber = self.request.user
        if author == subscriber:
            return Response(
                data={'errors': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
            author=author,
            subscriber=subscriber
        ).exists():
            return Response(
                data={'errors': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(
            data={
                'author': author.pk,
                'subscriber': subscriber.pk
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscriber = self.request.user
        if author == subscriber:
            return Response(
                data={'errors': 'Нельзя отписаться от самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscripton = Follow.objects.filter(
            author=author,
            subscriber=subscriber
        )
        if not subscripton.exists():
            return Response(
                data={'errors': 'Вы не были подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscripton.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)