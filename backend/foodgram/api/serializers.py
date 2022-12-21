from rest_framework import serializers
from recipes.models import Ingredient, Recipes, Tag, IngredientAmount
from drf_writable_nested.serializers import WritableNestedModelSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'color', 'slug')
        model = Tag
        lookup_fields = 'slug'

        def validate(self, data):
            if data == {}:
                raise serializers.ValidationError(
                    'Данные не корректны')
            return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'measurement_unit')
        model = Ingredient
        lookup_fields = 'name'

        def validate(self, data):
            if data == {}:
                raise serializers.ValidationError(
                    'Данные не корректны')
            return data


class IngredientAmountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('ingredient', 'amount')
        model = IngredientAmount
        lookup_fields = 'ingredient'

        def validate(self, data):
            if data == {}:
                raise serializers.ValidationError(
                    'Данные не корректны')
            return data


class RecipesSerializer(WritableNestedModelSerializer):
    ingredients = IngredientAmountSerializer(many=False)
    # tegs = serializers.PrimaryKeyRelatedField(
    #     queryset=Teg.objects.all(), many=True
    # )

    class Meta:
        fields = (
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'tags',
            'cooking_time')
        model = Recipes
        lookup_fields = 'name'

        def validate(self, data):
            if data == {}:
                raise serializers.ValidationError(
                    'Данные не корректны')
            return data
