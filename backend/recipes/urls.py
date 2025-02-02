from django.urls import path

from recipes.views import RedirectToRecipeView

urlpatterns = [
    path(
        "<str:short_link>/",
        RedirectToRecipeView.as_view(),
        name="short_link_redirect",
    ),
]
