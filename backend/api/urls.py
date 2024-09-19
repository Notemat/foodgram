from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    FavoriteViewSet, download_shopping_cart, RecipeViewSet,
    ShoppingCartViewSet, TagViewset, IngredientViewSet
)

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewset, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(v1_router.urls))
]
