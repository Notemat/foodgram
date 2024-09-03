from rest_framework import serializers

from recipes.models import Ingridient, Recipe, Tag


class RecipeSerializer(serializers.Serializer):
    """Сериализатор модели рецепта."""

    class Meta:

        fields = (
            'author', 'name', 'image',
            'text', 'ingridients', 'tags',
            'cooking_time', 'pub_date'
        )
        model = Recipe


class TagSerializer(serializers.Serializer):
    """Сериализатор для модели тэга."""

    class Meta:

        fields = ('name', 'slug')
        model = Tag


class IngridientSerializer(serializers.Serializer):
    """Сериализатор модели ингридиентов."""

    class Meta:

        fields = ('name', 'measurement_unit')
        model = Ingridient
