import pytest

from recipes.models import Recipe
from tests.constants import RECIPE_URL, FORMAT, RECIPES_COUNT


@pytest.mark.django_db
class TestRecipe:
    FILTER_RESULT = 1

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = \
            authenticated_client

    @pytest.fixture(autouse=True)
    def setup_second_authenticated_client(self, second_authenticated_client):
        """
        Вызываем фикстуру второго авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.second_authenticated_client, self.second_authenticated_data = \
            second_authenticated_client

    @pytest.fixture(autouse=True)
    def create_ingredients(self, create_ingredients):
        """Вызываем фикстуру ингредиентов."""
        self.ingredients_data = create_ingredients

    @pytest.fixture(autouse=True)
    def create_tags(self, create_tags):
        """Вызываем фикстуру тэгов."""
        self.tags_data = create_tags

    @pytest.fixture
    def update_data(self):
        return {
            'ingredients': [{'id': 1, 'amount': 6}],
            'tags': [1],
            'name': 'string02',
            'text': 'string02',
            'cooking_time': 5
        }

    @pytest.fixture
    def create_recipe(self, setup_data, setup_authenticated_client):
        """Создаем рецепт в базе данных."""

        recipe = setup_data.copy()
        recipe['name'] = 'first_recipe'
        response = self.authenticated_client.post(
            RECIPE_URL, recipe, format=FORMAT
        )
        return response

    def test_create_recipe(self, setup_data):
        """Тестируем создание рецепта авторизированным пользователем."""
        response = self.authenticated_client.post(
            RECIPE_URL, setup_data, format=FORMAT
        )
        assert response.status_code == 201
        assert response.data['name'] == setup_data['name']
        assert Recipe.objects.filter(name=setup_data['name']).exists()

    def test_unauthorized_user_create_recipe(self, setup_data, client):
        """
        Проверяем, что навторизированный пользователь
        не может создавать рецепт.
        """
        response = client.post(RECIPE_URL, setup_data, format=FORMAT)
        assert response.status_code == 401

    def test_create_recipe_without_field(self, setup_data):
        """Проверяем, что невозможно создать рецепт с пустым полем"""
        required_fields = [
            'name', 'ingredients', 'tags', 'text', 'cooking_time'
        ]
        for field in required_fields:
            data = setup_data.copy()
            data.pop(field)
            response = self.authenticated_client.post(
                RECIPE_URL, data, format=FORMAT
            )
            assert response.status_code == 400
            assert 'Обязательное поле' in str(response.data[field][0])

    def test_get_list_recipes(self, client, create_recipes):
        """Проверяем доступность списка рецептов"""
        response = client.get(RECIPE_URL)
        assert response.status_code == 200
        assert 'results' in response.data

        recipes = response.data['results']
        assert len(recipes) == RECIPES_COUNT

    def test_get_recipe(self, client, create_recipes):
        """Проверяем доступность конкретного рецепта."""
        for recipe in create_recipes:
            recipe_id = recipe['id']
            response = client.get(f'{RECIPE_URL}{recipe_id}/')
            assert response.status_code == 200
            assert response.data['id'] == recipe_id

    def test_putch_recipe(self, create_recipe, update_data):
        """Проверяем возможность обновления рецепта."""
        recipe_id = create_recipe.data['id']
        response = self.authenticated_client.patch(
            f'{RECIPE_URL}{recipe_id}/', update_data, format='json'
        )
        assert response.status_code == 200
        assert response.data['name'] == update_data['name']

    def test_not_author_cant_putch_recipe(self, create_recipe, update_data):
        """Проверяем, что пользователь не может обновлять чужие рецепты."""
        recipe_id = create_recipe.data['id']
        response = self.second_authenticated_client.patch(
            f'{RECIPE_URL}{recipe_id}/', update_data, format='json'
        )
        assert response.status_code == 403

    def test_unauthorized_user_cant_putch_recipe(
        self, client, create_recipe, update_data
    ):
        """
        Проверяем, что неавторизированный пользователь
        не может обновлять чужие рецепты.
        """
        recipe_id = create_recipe.data['id']
        response = client.patch(
            f'{RECIPE_URL}{recipe_id}/', update_data, format='json'
        )
        assert response.status_code == 401

    def test_delete_recipe(self, create_recipe, update_data):
        """Проверяем возможность удаления рецепта."""
        recipe_id = create_recipe.data['id']
        response = self.authenticated_client.delete(
            f'{RECIPE_URL}{recipe_id}/', update_data, format='json'
        )
        assert response.status_code == 204
        assert response.data is None

    def test_not_author_cant_delete_recipe(self, create_recipe, update_data):
        """Проверяем, что пользователь не может удалить чужой рецепт."""
        recipe_id = create_recipe.data['id']
        response = self.second_authenticated_client.delete(
            f'{RECIPE_URL}{recipe_id}/', update_data, format='json'
        )
        assert response.status_code == 403

    def test_unauthorized_user_cant_delete_recipe(
        self, client, create_recipe, update_data
    ):
        """
        Проверяем, что неавторизированный пользователь
        не может удалить чужой рецепт.
        """
        recipe_id = create_recipe.data['id']
        response = client.delete(
            f'{RECIPE_URL}{recipe_id}/', update_data, format='json'
        )
        assert response.status_code == 401

    def test_get_link(self, create_recipe):
        """Проверяем доступность короткой ссылки на рецепт."""
        recipe_id = create_recipe.data['id']
        response = self.authenticated_client.get(
            f'{RECIPE_URL}{recipe_id}/get-link/'
        )
        assert response.status_code == 200
        assert 'short-link' in response.data

    def test_filter_by_favorited(self, create_favorite, first_recipe_id):
        """Проверяем фильтрацию рецептов по избранному."""
        response = self.second_authenticated_client.get(
            f'{RECIPE_URL}?is_favorited=1'
        )
        assert response.status_code == 200
        assert len(response.data['results']) == self.FILTER_RESULT
        assert response.data['results'][0]['id'] == first_recipe_id

    def test_filter_by_is_in_shopping_cart(
            self, create_shopping_cart, first_recipe_id
    ):
        """Проверяем фильтрацию рецепта по списку покупок."""
        response = self.second_authenticated_client.get(
            f'{RECIPE_URL}?is_in_shopping_cart=1'
        )
        assert response.status_code == 200
        assert len(response.data['results']) == self.FILTER_RESULT
        assert response.data['results'][0]['id'] == first_recipe_id

    def test_filter_by_author(self, create_recipes, first_recipe_id):
        """Проверяем фильтрацию рецептов по автору"""
        response = self.second_authenticated_client.get(
            f'{RECIPE_URL}?author=1'
        )
        assert response.status_code == 200
        assert len(response.data['results']) == self.FILTER_RESULT
        assert response.data['results'][0]['id'] == first_recipe_id

    def test_filter_by_tags(self, create_recipes, first_recipe_id):
        """Проверяем фильтрацию рецептов по автору"""
        response = self.second_authenticated_client.get(
            f'{RECIPE_URL}?tags=tag01&tag02'
        )
        assert response.status_code == 200
        print(response.data['results'])
        assert len(response.data['results']) == self.FILTER_RESULT
        assert response.data['results'][0]['id'] == first_recipe_id
