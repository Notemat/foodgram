from django.urls import path

from recipes.views import RedirectToRecipeView, ShortLinkView

urlpatterns = [
    path(
        "<s/str:short_link>/",
        ShortLinkView.as_view(),
        name="short_link",
    ),
    path(
        "<str:short_link>/",
        RedirectToRecipeView.as_view(),
        name="short_link_redirect",
    ),
    
]
