from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers import (
    IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, TagSerializer
)
from api.permissions import AuthorOrReadOnlyPermission
from recipes.models import Ingredient, Recipe, Tag


def redirect_to_recipe(request, short_link):
    """Функция для редиректа по короткой ссылке."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return HttpResponseRedirect(f'/recipies/{recipe.short_link}/')


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        """Выбираем соответствующий запросу сериализатор."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        """Выбираем пермишен для обновления или удаления рецепта."""
        if self.request.method == 'PATCH' or self.request.method == 'DELETE':
            permission_classes = (AuthorOrReadOnlyPermission,)
            return [permission() for permission in permission_classes]
        permission_classes = (IsAuthenticatedOrReadOnly,)
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Сохраняем автора поста."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Получаем короткую ссылку на рецепт."""
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/r/{recipe.short_link}')
        return Response({'short_link': link}, status=status.HTTP_200_OK)


class TagViewset(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
