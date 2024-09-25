from django.http import HttpResponse

from api.constants import (
    FALSE,
    LINE_SPACING,
    START_Y,
    TEXT_FONT_SIZE,
    TEXT_X,
    TITLE_FONT_SIZE,
    TITLE_X,
    TITLE_Y,
    TRUE,
)
from api.mixins import ShoppingCartFavoriteViewSetMixin
from api.permissions import AuthorOrReadOnlyPermission
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def download_shopping_cart(request):
    """Функция для выгрузки списка покупок pdf-документом."""
    ingredients = get_aggregatted_ingridients(request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="shoppinglist.pdf"'
    p = canvas.Canvas(response)
    pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

    p.setFont("DejaVuSans", TITLE_FONT_SIZE)
    p.drawString(TITLE_X, TITLE_Y, "Список покупок")

    p.setFont("DejaVuSans", TEXT_FONT_SIZE)
    y = START_Y
    for ingredient, data in ingredients.items():
        p.drawString(
            TEXT_X,
            y,
            f"{ingredient} ({data['measurement_unit']}) "
            f"— {data['amount']}",
        )
        y -= LINE_SPACING

    p.showPage()
    p.save()
    return response


def get_aggregatted_ingridients(user):
    """Получаем ингридиенты для списка покупок."""
    recipies = Recipe.objects.filter(shoppingcart__user=user)
    ingredients = {}

    for recipe in recipies:
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            if ingredient.name in ingredients:
                ingredients[ingredient.name]["amount"] += (
                    recipe_ingredient.amount
                )
            else:
                ingredients[ingredient.name] = {
                    "amount": recipe_ingredient.amount,
                    "measurement_unit": ingredient.measurement_unit,
                }
    return ingredients


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)

    def get_queryset(self):
        """Переопределяем queryset для возможности сортировки выдачи."""
        queryset = Recipe.objects.all()

        author = self.request.query_params.get("author")
        tags = self.request.query_params.getlist("tags")
        is_favorited = self.request.query_params.get("is_favorited")
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )

        if author:
            queryset = queryset.filter(author__id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        user = self.request.user
        if user.is_authenticated:
            if is_favorited:
                if is_favorited == TRUE:
                    queryset = queryset.filter(favorite__user=user)
                elif is_favorited == FALSE:
                    queryset = queryset.exclude(favorite__user=user)
            if is_in_shopping_cart:
                if is_in_shopping_cart == TRUE:
                    queryset = queryset.filter(shoppingcart__user=user)
                elif is_in_shopping_cart == FALSE:
                    queryset = queryset.exclude(shoppingcart__user=user)
        return queryset

    def get_serializer_context(self):
        """Добавляем контекст для сериализатора."""
        return {"request": self.request}

    def get_serializer_class(self):
        """Выбираем соответствующий запросу сериализатор."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        """Выбираем пермишен для обновления или удаления рецепта."""
        if self.request.method == "PATCH" or self.request.method == "DELETE":
            permission_classes = (AuthorOrReadOnlyPermission,)
            return [permission() for permission in permission_classes]
        permission_classes = (IsAuthenticatedOrReadOnly,)
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Сохраняем автора."""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Обрабатываем и сохраняем данные сериализатора для записи.

        Используем сериализатор для чтения для отображения ответа.
        """
        serializer = RecipeWriteSerializer(
            data=request.data, context={"request": self.request}
        )
        if serializer.is_valid():
            self.perform_create(serializer)
            response_serializer = RecipeReadSerializer(
                serializer.instance, context={"request": self.request}
            )
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Для обновления рецепта используем сериализатор для записи.

        Для ответа - сериализатор для чтения.
        """
        partial = request.method == "PATCH"
        instance = self.get_object()
        serializer = RecipeWriteSerializer(
            instance, data=request.data,
            partial=partial, context={"request": request}
        )
        if serializer.is_valid():
            self.perform_update(serializer)
            response_serializer = RecipeReadSerializer(
                serializer.instance, context={"request": request}
            )
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        """Получаем короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_link = recipe.short_link
        if not short_link:
            short_link = recipe.generate_short_link()
            recipe.short_link = short_link
            recipe.save()

        link = request.build_absolute_uri(f"/r/{short_link}")
        return Response({"short-link": link}, status=status.HTTP_200_OK)


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
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ("id",)
    search_fields = ("^name",)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class ShoppingCartViewSet(ShoppingCartFavoriteViewSetMixin):
    """Вьюсет для списка покупок."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        return self.create_from_mixin(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Сохраняем автора и рецепт."""
        return self.perform_create_from_mixin(serializer=serializer)

    def delete(self, request, *args, **kwargs):
        """Удаляем объект из избранного."""
        return self.delete_from_mixin(
            request, model_class=ShoppingCart, *args, **kwargs
        )


class FavoriteViewSet(ShoppingCartFavoriteViewSetMixin):
    """Вьюсет для избранного."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def create(self, request, *args, **kwargs):
        return self.create_from_mixin(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Сохраняем автора и рецепт."""
        return self.perform_create_from_mixin(serializer=serializer)

    def delete(self, request, *args, **kwargs):
        """Удаляем объект из избранного."""
        return self.delete_from_mixin(
            request, model_class=Favorite, *args, **kwargs
        )
