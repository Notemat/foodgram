from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.serializers import RecipeReadShortSerializer
from recipes.models import Recipe


class RecipeSerializerMixin(serializers.ModelSerializer):
    """Миксин для сериализаторов избранного и списка покупок."""

    recipe = RecipeReadShortSerializer(read_only=True)

    class Meta:
        fields = ('recipe',)

    def validate_recipe_in_user(self, model_class, error_message):
        """Валидация подписки на пользователя."""
        user = self.context['request'].user
        recipe = self.context['view'].kwargs.get('recipe_id')
        if model_class.objects.filter(
            user=user, recipe=get_object_or_404(Recipe, id=recipe)
        ).exists():
            raise serializers.ValidationError(error_message)
        return self.initial_data

    def to_representation(self, instance):
        """Возвращаем в ответе словарь объектов."""
        data = super().to_representation(instance)
        return data['recipe']
