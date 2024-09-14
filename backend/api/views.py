from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from reportlab.pdfgen import canvas

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, serializers, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import (
    SAFE_METHODS, IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingCartSerializer, TagSerializer
)
from api.permissions import AuthorOrReadOnlyPermission
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    """Функция для выгрузки pdf-документа."""
    ingredients = get_aggregatted_ingridients(request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 100, 'Shopping_list')
    y = 700
    for ingredient, data in ingredients.items():
        p.drawString(
            100, y, f"{ingredient} ({data['measurement_unit']}) — {data['amount']}"
        )
        y -= 20

    p.showPage()
    p.save()

    return response


def get_aggregatted_ingridients(user):
    """Получаем ингридиенты для списка."""
    recipies = Recipe.objects.filter(shoppingcart__user=user)
    ingredients = {}

    for recipe in recipies:
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            if ingredient.name in ingredients:
                ingredients[ingredient.name]['amount'] += (
                    ingredient.recipeingredient.amount
                )
            else:
                ingredients[ingredient.name] = {
                    'amount': recipe_ingredient.amount,
                    'measurement_unit': ingredient.measurement_unit
                }
    return ingredients


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
        """Сохраняем автора."""
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
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет для списка покупок."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        """Сохраняем автора."""
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        if ShoppingCart.objects.filter(
            user=self.request.user, recipe=recipe
        ).exists():
            raise serializers.ValidationError("Этот рецепт уже в корзине.")

        serializer.save(user=self.request.user, recipe=recipe)


class FavoriteViewSet(
    CreateModelMixin, DestroyModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для избранного."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """Сохраняем автора и рецепт."""
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        serializer.save(user=self.request.user, recipe=recipe)

    def delete(self, request, *args, **kwargs):
        """Удаляем объект из избранного."""
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        favorite = get_object_or_404(
            Favorite, user=self.request.user, recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
