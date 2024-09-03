from django.shortcuts import render

from rest_framework import viewsets

from api.serializers import (
    IngridientSerializer, RecipeSerializer, TagSerializer
)
from recipes.models import Ingridient, Recipe, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewset(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингридиентов."""

    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    pagination_class = None
