from django.shortcuts import get_object_or_404, render

from rest_framework import status, viewsets
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers import (
    IngridientSerializer, RecipeReadSerializer, RecipeWriteSerializer, TagSerializer
)
from recipes.models import Ingridient, Recipe, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = RecipeReadSerializer

    def create(self, request, *args, **kwargs):
        """
        Переопределение метода создания рецепта.
        """

        serializer = RecipeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def get_ingridient_object(self):
    #     title_id = self.kwargs.get('ingridient_id')
    #     return get_object_or_404(Ingridient, pk=title_id)

    def perform_create(self, serializer):
        """Сохраняем автора поста."""
        serializer.save(
            author=self.request.user,
            # ingridient=self.get_ingridient_object()
        )


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
