from django.urls import include, path

from api.views import (
    FavoriteViewSet,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewset,
    download_shopping_cart,
)
from rest_framework.routers import DefaultRouter

v1_router = DefaultRouter()
v1_router.register("recipes", RecipeViewSet, basename="recipes")
v1_router.register("tags", TagViewset, basename="tags")
v1_router.register("ingredients", IngredientViewSet, basename="ingredients")
v1_router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
v1_router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    FavoriteViewSet, basename="favorite"
)


urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        download_shopping_cart,
        name="download_shopping_cart",
    ),
    path("s/", include(v1_router.urls)),
]
