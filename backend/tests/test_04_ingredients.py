import pytest

from recipes.models import Ingredient


@pytest.mark.django_db
class TestIngredient:

    INGREDIENT_URL = "/api/ingredients/"
    COUNT_ING_NAME_OBJECTS = 2

    @pytest.fixture(autouse=True)
    def create_ingredients(self, create_ingredients):
        """Вызываем фикстуру ингредиентов."""
        self.ingredients_data = create_ingredients

    def test_get_list_ingredients(self, client):
        """Проверяем доступность списка ингредиентов."""
        ingredients_count = Ingredient.objects.count()
        response = client.get(self.INGREDIENT_URL)
        assert response.status_code == 200
        response_count = len(response.data)
        assert response_count == ingredients_count

    def test_get_ingredient(self, client, create_ingredients):
        """Проверяем доступность отдельного ингредиента."""
        ingredient = Ingredient.objects.latest("id")
        ingredient_id = ingredient.id
        response = client.get(f"{self.INGREDIENT_URL}{ingredient_id}/")
        assert response.status_code == 200
        assert "name" in response.data

    def test_search_ingredient_by_partial_name(self, client):
        """Проверяем поиск ингредиента по начальной части названия."""
        search_term = "ing"
        response = client.get(f"{self.INGREDIENT_URL}?search={search_term}")

        assert response.status_code == 200
        results = response.data
        assert len(results) == self.COUNT_ING_NAME_OBJECTS
        assert results[0]["name"].startswith(search_term)
        assert results[1]["name"].startswith(search_term)
