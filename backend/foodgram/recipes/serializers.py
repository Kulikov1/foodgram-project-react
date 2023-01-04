from rest_framework import serializers
# from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, Tag, IngredientAmount, Follow
from users.serializers import CustomUserSerializer
# from rest_framework.validators import ValidationError

# from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'color', 'slug')
        model = Tag
        lookup_fields = 'slug'
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов"""

    tags = serializers.SerializerMethodField()
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredienttorecipe')
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )
    read_only_fields = ('id', 'author', 'is_favorited',
                        'is_favorited')

    def get_tags(self, obj):
        return TagSerializer(
            Tag.objects.filter(recipes=obj),
            many=True,).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов"""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredienttorecipe')

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

            if 'ingredienttorecipe' in data:
                ingredients = data['ingredienttorecipe']
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

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_obj = Ingredient.objects.get(
                id=ingredient_data.get('ingredient')['id'])
            ingredient_liist.append(
                IngredientAmount(
                    ingredient=ingredient_obj,
                    amount=ingredient_data.get('amount'),
                    recipe=recipe,
                )
            )
        IngredientAmount.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('Ingredientamount')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('Ingredientamount')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
                 'request': self.context.get('request')
            }).data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')