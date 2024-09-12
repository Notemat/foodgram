from rest_framework import serializers

from recipes.models import Recipe


class RecipeReadShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого чтения рецепта."""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe