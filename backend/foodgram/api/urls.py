from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipesViewSet,
    FollowViewSet,
    ListOnlyFollowsAPIView
)

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/<int:users_id>/subscribe/', FollowViewSet.as_view(
            {
                'post': 'create',
                'delete': 'destroy'
            }
        )
    ),
    path(
        'users/subscriptions/',
        ListOnlyFollowsAPIView.as_view(),
        name='users-follow'
    ),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]