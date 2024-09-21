import pytest

@pytest.mark.django_db
class TestRecipe:
    RECIPE_URL = '/api/recipes/'