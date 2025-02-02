import pytest
from tests.constants import RECIPE_URL, SHOPPING_CART_URL


@pytest.mark.django_db
class TestShoppingCart:

    DOWNLOAD_SHOPPING_CART = "/api/recipes/download_shopping_cart/"

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = (
            authenticated_client
        )

    @pytest.fixture(autouse=True)
    def setup_second_authenticated_client(self, second_authenticated_client):
        """
        Вызываем фикстуру второго авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.second_authenticated_client, self.second_authenticated_data = (
            second_authenticated_client
        )

    def test_01_get_shopping_cart_list(self, create_shopping_cart):
        """Проверяем возможность скачать список покупок."""
        response = self.second_authenticated_client.get(
            self.DOWNLOAD_SHOPPING_CART
        )
        assert response.status_code == 200

        assert response["Content-Type"] == "application/pdf"

    def test_02_unauthorized_user_cant_get_shopping_cart_list(
        self, client, create_shopping_cart
    ):
        """
        Проверяем, что неавторизированный пользователь
        не может скачать список покупок.
        """
        response = client.get(self.DOWNLOAD_SHOPPING_CART)
        assert response.status_code == 401
        assert "detail" in response.data

    def test_03_create_shopping_cart(self, create_recipes, first_recipe_id):
        """Проверяем возможность добавить рецепт в избранное."""
        response = self.second_authenticated_client.post(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert response.status_code == 201
        assert "id" in response.data
        assert "name" in response.data
        assert "image" in response.data
        assert "cooking_time" in response.data

    def test_04_not_twice_create_shopping_cart(
        self, create_recipes, first_recipe_id
    ):
        """Проверяем, что нельзя добавить рецепт в избранное дважды."""
        response = self.second_authenticated_client.post(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert response.status_code == 201

        second_response = self.second_authenticated_client.post(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert second_response.status_code == 400
        assert "errors" in second_response.data

    def test_05_unauthorized_user_cant_create_recipe(
        self, client, create_recipes, first_recipe_id
    ):
        """
        Проверяем, что неавторизованный пользователь
        не может добавлять рецепты в избранное.
        """
        response = client.post(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert response.status_code == 401
        assert "detail" in response.data

    def test_06_delete_shopping_cart(
        self, create_shopping_cart, first_recipe_id
    ):
        """Проверяем возможность удалить рецепт из избранного."""
        response = self.second_authenticated_client.delete(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert response.status_code == 204
        assert response.data is None

    def test_07_cant_delete_not_shopping_cart(
        self, create_recipes, first_recipe_id
    ):
        """
        Проверяем, что нельзя удалить рецепт из избранного,
        если его там нет.
        """
        response = self.second_authenticated_client.delete(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert response.status_code == 400
        assert "errors" in response.data

    def test_08_unauthorized_user_cant_delete_shopping_cart(
        self, client, create_recipes, first_recipe_id
    ):
        """
        Проверяем, что неавторизованный пользователь
        не может удалять рецепты из избранного.
        """
        response = client.delete(
            f"{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}"
        )
        assert response.status_code == 401
        assert "detail" in response.data
