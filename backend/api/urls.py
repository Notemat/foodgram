from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet, TagViewset, IngridientViewSet

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewset, basename='tags')
v1_router.register('ingridients', IngridientViewSet, basename='ingridients')


urlpatterns = [
    path('', include(v1_router.urls))
]