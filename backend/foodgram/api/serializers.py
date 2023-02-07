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


class ReadOnlyIngredientsAmountSerializer(serializers.ModelSerializer):
    """Класс количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


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
    ingredients = ReadOnlyIngredientsAmountSerializer(
        many=True,
        source='ingredientamount_set')
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
    ingredients = CreateIngredientsAmountSerializer(
        read_only=False,
        many=True,
        required=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())

    class Meta:
        depth = 3
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        ]

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!')
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!')
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1!')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredient_objects = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            recipe_ingredient_object = IngredientAmount(
                recipe=recipe,
                ingredient=ingredient_id,
                amount=amount
            )
            recipe_ingredient_objects.append(recipe_ingredient_object)
        IngredientAmount.objects.bulk_create(recipe_ingredient_objects)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return ReadOnlyRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class RecipePartInfoSerializer(serializers.ModelSerializer):
    """Класс рецептов с минимальным количеством информации."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """Класс получения данных подписок на авторов."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def check_is_subscribed(self, subscription):
        current_user = self.context.get('request').user
        return Follow.objects.filter(
            author=subscription.author,
            subscriber=current_user
        ).exists()

    def get_recipes(self, value):
        serialized_recipes = []
        recipes = Recipe.objects.filter(author=value)
        for recipe in recipes:
            serialized_recipe = RecipePartInfoSerializer(recipe)
            serialized_recipes.append(serialized_recipe.data)
        return serialized_recipes

    def get_recipes_count(self, value):
        return len(Recipe.objects.filter(author=value))


class FollowSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionSerializer(
            instance,
            context=context
        )
        return serializer.data

    class Meta:
        model = Follow
        fields = '__all__'
