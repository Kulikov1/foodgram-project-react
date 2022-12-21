from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserCreateViewSet, TokenViewSet

app_name = 'users'

router = router_auth = DefaultRouter()
router.register('users', UserViewSet)
router_auth.register('signup', UserCreateViewSet)
router_auth.register('token', TokenViewSet, basename='token')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(router_auth.urls)),
]
