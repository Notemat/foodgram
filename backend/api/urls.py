from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    RecipeViewSet, redirect_to_recipe, TagViewset, IngredientViewSet
)

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewset, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('r/<str:short_link>', redirect_to_recipe, name='recipe_short_link'),
    path('', include(v1_router.urls))
]