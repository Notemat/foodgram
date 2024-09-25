from recipes.models import Recipe
from rest_framework.serializers import ModelSerializer


class RecipeReadShortSerializer(ModelSerializer):
    """Сериализатор для короткого чтения рецепта."""

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe
