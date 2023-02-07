from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipesViewSet,
    FollowView,
    ListOnlyFollowAPIView
)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipesViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/<int:pk>/subscribe/',
        FollowView.as_view(),
        name='users-detail-subscribe'
    ),
    path(
        'users/subscriptions/',
        ListOnlyFollowAPIView.as_view(),
        name='users-subscribtions'
    ),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]