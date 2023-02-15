from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import SerializerMethodField
from django.contrib.auth import get_user_model

from recipes.models import (
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
)
from users.models import Follow

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор отображения юзера в соответствии с ТЗ"""

    is_subscribed = SerializerMethodField()

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user

        return Follow.objects.filter(
            user=current_user.id,
            author=obj.id).exists()



class IngredientSerializer(serializers.ModelSerializer):
    """Класс ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ReadOnlyIngredientAmountSerializer(serializers.ModelSerializer):
    """Класс количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount', 'name', 'measurement_unit')


class CreateIngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        read_only=False,
    )

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингердиентов не может быть меньше единицы!'
            )
        return value

    class Meta:
        model = IngredientAmount
        fields = ['id', 'amount']


class TagSerializer(serializers.ModelSerializer):
    """Класс тэгов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(many=False)
    ingredients = ReadOnlyIngredientAmountSerializer(
        many=True,
        source='ingredientamount',
        )
    is_favorited = serializers.SerializerMethodField(
        method_name='check_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='check_is_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        read_only_fields = ['__all__']
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]
    
    def is_in_list(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def check_is_favorited(self, recipe):
        return self.is_in_list(recipe, Favorite)

    def check_is_in_shopping_cart(self, recipe):
        return self.is_in_list(recipe, ShoppingCart)


class CreateOrUpdateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = CreateIngredientsAmountSerializer(
        many=True,
        source='ingredientamount')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        request = self.context.get('request', None)
        tags_list = []
        ingredients_list = []
        request_methods = ['POST', 'PATCH']

        if request.method in request_methods:
            if 'tags' in data:
                tags = data['tags']

                for tag in tags:
                    if tag.id in tags_list:
                        raise serializers.ValidationError(
                            F'Тег {tag} повторяется')
                    tags_list.append(tag.id)

                if len(tags_list) == 0:
                    raise serializers.ValidationError(
                            'Список тегов не должен быть пустым')

                all_tags = Tag.objects.all().values_list('id', flat=True)
                if not set(tags_list).issubset(all_tags):
                    raise serializers.ValidationError(
                        F'Тега {tag} не существует')

            if 'ingredients' in data:
                ingredients = data['ingredients']
                for ingredient in ingredients:
                    ingredient = ingredient['ingredient'].get('id')

                    if ingredient in ingredients_list:
                        raise serializers.ValidationError(
                            F'Ингредиент {ingredient} повторяется')
                    ingredients_list.append(ingredient)

                all_ingredients = Ingredient.objects.all().values_list(
                    'id', flat=True)

                if not set(ingredients_list).issubset(all_ingredients):
                    raise serializers.ValidationError(
                        'Указанного ингредиента не существует')

                if len(ingredients_list) == 0:
                    raise serializers.ValidationError(
                            'Список ингредиентов не должен быть пустым')
        return data

    def create_ingredients(self, recipe, ingredients):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            recipe_ingredient_object = IngredientAmount(
                recipe=recipe,
                ingredient=ingredient_id,
                amount=amount
            )
            ingredient_list.append(recipe_ingredient_object)
        IngredientAmount.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientamount')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredientamount')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadOnlyRecipeSerializer(instance, context={
                 'request': self.context.get('request')
            }).data


class RecipePartInfoSerializer(serializers.ModelSerializer):
    """Класс рецептов с минимальным количеством информации."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowCreateSerializer(CustomUserSerializer):
    """Класс получения данных подписок на авторов."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, follow):
        current_user = self.context.get('request').user
        return Follow.objects.filter(
            author=follow.author,
            user=current_user
        ).exists()

    def get_recipes(self, follow):
        queryset = Recipe.objects.filter(author=follow.author)
        serializer = RecipePartInfoSerializer(
            queryset,
            read_only=True,
            many=True
        )
        return serializer.data

    def get_recipes_count(self, follow):
        return Recipe.objects.filter(author=follow.author).count()


class FollowSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = FollowCreateSerializer(
            instance,
            context=context
        )
        return serializer.data

    class Meta:
        model = Follow
        fields = '__all__'
