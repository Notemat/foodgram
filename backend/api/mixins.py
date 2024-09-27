from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Recipe
from recipes.serializers import RecipeReadShortSerializer


class ShoppingCartFavoriteSerializerMixin(serializers.ModelSerializer):
    """Миксин для сериализаторов избранного и списка покупок."""

    recipe = RecipeReadShortSerializer(read_only=True)

    class Meta:
        fields = ("recipe",)

    def create_recipe_and_user(self, model_class, validated_data):
        """Переопределение метода create для корректного сохранения объекта."""
        user = self.context["request"].user
        recipe = self.context["view"].kwargs.get("recipe_id")
        recipe_instance = get_object_or_404(Recipe, id=recipe)
        return model_class.objects.create(user=user, recipe=recipe_instance)

    def validate_recipe_and_user(self, model_class, error_message):
        """Валидация подписки на пользователя."""
        user = self.context["request"].user
        recipe = self.context["view"].kwargs.get("recipe_id")
        if model_class.objects.filter(
            user=user, recipe=get_object_or_404(Recipe, id=recipe)
        ).exists():
            raise serializers.ValidationError(error_message)
        return self.initial_data

    def to_representation(self, instance):
        """Возвращаем в ответе словарь объектов."""
        data = super().to_representation(instance)
        return data["recipe"]


class ShoppingCartFavoriteViewSetMixin(
    CreateModelMixin, DestroyModelMixin, viewsets.GenericViewSet
):
    """Миксин для вьюсетов списка покупок и избранного."""

    permission_classes = (IsAuthenticated,)

    def create_from_mixin(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create_from_mixin(self, serializer):
        """Сохраняем автора и рецепт."""
        recipe_id = self.kwargs.get("recipe_id")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    def delete_from_mixin(self, request, model_class, *args, **kwargs):
        """Удаляем объект из списка."""
        recipe = get_object_or_404(Recipe, id=self.kwargs["recipe_id"])
        is_in_shopping_cart = model_class.objects.filter(
            user=self.request.user, recipe=recipe
        )
        if not is_in_shopping_cart:
            return Response(
                {"errors": "Рецепт еще не добавлен добавлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        is_in_shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
