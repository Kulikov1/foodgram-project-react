from .models import User
from rest_framework import serializers, validators


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())],
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserEditSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'username',)

    def validate(self, data):
        if data['username'] == data['email']:
            raise serializers.ValidationError(
                'Поля "username" и "email" должны быть различны'
            )
        return data

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                '"me" не может быть именем пользователя'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.SlugField(required=True)
    confirmation_code = serializers.SlugField(required=True)
