from django.shortcuts import get_object_or_404
from .models import User
from .serializers import (
    UserSerializer,
    UserEditSerializer,
    UserCreateSerializer,
    TokenSerializer
)
from rest_framework import viewsets, permissions, status, mixins
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import AccessToken
from foodgram.settings import DEFAULT_FROM_EMAIL


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class UserCreateViewSet(CreateViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        username = request.data['username']
        user = get_object_or_404(User, username=username)
        address_to = request.data['email']
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Регистрация YamDB',
            message=f'Код подтверждения: {confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[address_to],
        )
        return Response(serializer.data, status=status.HTTP_200_OK,
                        headers=headers)


class TokenViewSet(CreateViewSet):
    serializer_class = TokenSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data['username']
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(
            user,
            request.data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response(f'Ваш токен: {token}', status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def user_own_profile(self, request):
        user = get_object_or_404(User, username=request.user)
        serializer = self.get_serializer(user, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        if request.method == 'PATCH':
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
