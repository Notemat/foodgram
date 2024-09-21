import pytest

from recipes.models import Ingredient, Tag


@pytest.mark.django_db
class TestRecipe:
    RECIPE_URL = '/api/recipes/'
    RECIPE_IMAGE = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///"
        "9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByx"
        "OyYQAAAABJRU5ErkJggg=="
    )
    FORMAT = 'json'

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = \
            authenticated_client

    @pytest.fixture(autouse=True)
    def create_db(self):
        """Создаем тэги и ингредиенты в базе данных."""
        Ingredient.objects.create(
            name='ingredient01', measurement_unit='measurement_unit01'
        )
        Ingredient.objects.create(
            name='ingredient02', measurement_unit='imeasurement_unit02'
        )
        Tag.objects.create(name='tag01', slug='tag01')
        Tag.objects.create(name='tag02', slug='tag02')
        Tag.objects.create(name='tag03', slug='tag03')

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Данные для создания рецепта."""
        return {
            "ingredients": [
                {
                    "id": 1,
                    "amount": 10
                }
            ],
            "tags":
            [
                1,
                2
            ],
            "image": self.RECIPE_IMAGE,
            "name": "string",
            "text": "string",
            "cooking_time": 1
        }

    def test_create_recipe(self, setup_data):
        """Тестируем создание рецепта авторизированным пользователем."""
        response = self.authenticated_client.post(
            self.RECIPE_URL, setup_data, format=self.FORMAT
        )
        assert response.status_code == 201
        assert response.data['name'] == setup_data['name']

    def test_unauthorized_user_create_recipe(self, setup_data, client):
        """
        Проверяем, что навторизированный пользователь
        не может создавать рецепт.
        """
        response = client.post(self.RECIPE_URL, setup_data, format=self.FORMAT)
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
                self.RECIPE_URL, data, format=self.FORMAT
            )
            assert response.status_code == 400
            assert 'Обязательное поле' in str(response.data[field][0])
