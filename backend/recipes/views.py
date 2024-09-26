from django.shortcuts import get_object_or_404, redirect
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe


class RedirectToRecipeView(View):
    """Вью для редиректа по короткой ссылке."""

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect(f"/recipes/{recipe.id}/")


class ShortLinkView(APIView):
    """Вью для получения короткой ссылки на рецепт."""

    def get(self, request, pk=None):
        """Получаем короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = recipe.short_link
        if not short_link:
            short_link = recipe.generate_short_link()
            recipe.short_link = short_link
            recipe.save()

        link = request.build_absolute_uri(f"{short_link}")
        return Response({"short-link": link}, status=status.HTTP_200_OK)
