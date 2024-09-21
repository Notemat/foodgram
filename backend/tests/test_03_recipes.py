import pytest

from recipes.models import Ingredient, Recipe, Tag


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
    RECIPES_COUNT = 2

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = \
            authenticated_client

    @pytest.fixture(autouse=True)
    def create_ingredients(self):
        """Создаем тэги и ингредиенты в базе данных."""
        ingredients_data = [
            {'name': 'ingredient01', 'measurement_unit': 'measurement_unit01'},
            {'name': 'ingredient02', 'measurement_unit': 'measurement_unit02'},
            {'name': 'ingredient03', 'measurement_unit': 'measurement_unit03'},
        ]
        for ingredient in ingredients_data:
            Ingredient.objects.get_or_create(**ingredient)

    @pytest.fixture(autouse=True)
    def create_tags(self):
        """Создаем тэги и ингредиенты в базе данных."""
        tags_data = [
            {"name": "tag01", "slug": "tag01"},
            {"name": "tag02", "slug": "tag02"},
            {"name": "tag03", "slug": "tag03"},
        ]
        for tag in tags_data:
            Tag.objects.get_or_create(**tag)

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Данные для создания рецепта."""
        return {
            'ingredients': [
                {
                    'id': 1,
                    'amount': 10
                }
            ],
            'tags':
            [
                1,
                2
            ],
            'image': self.RECIPE_IMAGE,
            'name': 'string01',
            'text': 'string01',
            'cooking_time': 1
        }
    
    @pytest.fixture
    def update_data(self):
        return {
            'ingredients': [
                {
                    'id': 2,
                    'amount': 6
                }
            ],
            'tags':
            [
                1
            ],
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
            self.RECIPE_URL, recipe, format=self.FORMAT
        )
        return response

    @pytest.fixture
    def create_recipes(self, setup_data, setup_authenticated_client):
        """Создаем рецепт в базе данных."""
        recipes = []

        first_recipe = setup_data.copy()
        first_recipe['name'] = 'first_recipe'
        first_response = self.authenticated_client.post(
            self.RECIPE_URL, first_recipe, format=self.FORMAT
        )
        recipes.append(first_response.data)

        second_recipe = setup_data.copy()
        second_recipe['name'] = 'second_recipe'
        second_response = self.authenticated_client.post(
            self.RECIPE_URL, second_recipe, format=self.FORMAT
        )
        recipes.append(second_response.data)
        return recipes

    def test_create_recipe(self, setup_data):
        """Тестируем создание рецепта авторизированным пользователем."""
        response = self.authenticated_client.post(
            self.RECIPE_URL, setup_data, format=self.FORMAT
        )
        assert response.status_code == 201
        assert response.data['name'] == setup_data['name']
        assert Recipe.objects.filter(name=setup_data['name']).exists()

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

    def test_get_list_recipes(self, client, create_recipes):
        """Проверяем доступность списка рецептов"""
        response = client.get(self.RECIPE_URL)
        assert response.status_code == 200
        assert 'results' in response.data

        recipes = response.data['results']
        assert len(recipes) >= self.RECIPES_COUNT

    def test_get_recipe(self, client, create_recipes):
        """Проверяем доступность конкретного рецепта."""
        for recipe in create_recipes:
            recipe_id = recipe['id']
            response = client.get(f'{self.RECIPE_URL}{recipe_id}/')
            assert response.status_code == 200
            assert response.data['id'] == recipe_id
    
    def test_putch_recipe(self, create_recipe, update_data):
        """Проверяем возможность обновления рецепта."""
        print(f'created_data  - {create_recipe.data}')
        print(f'update_data -  {update_data}')
        print(f'second_ingredient - {Ingredient.objects.filter(id=2)}')
        recipe_id = create_recipe.data['id']
        response = self.authenticated_client.patch(
            f'{self.RECIPE_URL}{recipe_id}/', update_data
        )
        print(response.data)
        assert response.status_code == 200
        assert response.data['name'] == update_data['name']

