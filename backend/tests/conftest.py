import pytest
from rest_framework.test import APIClient

from recipes.models import Tag, Ingredient, Recipe, User
from tests.constants import (
    USER_URL, URL_GET_LOGIN, CURRENT_PASSWORD,
    RECIPE_URL, RECIPE_IMAGE, FORMAT, FAVORITE_URL,
    SHOPPING_CART_URL
)


@pytest.fixture()
def unauthorized_client():
    """
    Фикстура неавторизированного клиента
    и данных для регистрации
    """
    client = APIClient()
    return client


@pytest.fixture()
def authenticated_client():
    """Фикстура авторизированного клиента."""
    client = APIClient()
    authenticated_data = {
        'email': 'test_user_02@yandex.ru',
        'username': 'test_user_02',
        'first_name': 'Иван',
        'last_name': 'Васильев',
        'password': CURRENT_PASSWORD
    }
    client.post(
        USER_URL, authenticated_data)
    login_response = client.post(
        URL_GET_LOGIN,
        {
            'email': authenticated_data['email'],
            'password': authenticated_data['password']
        }
    )
    token = login_response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client, authenticated_data


@pytest.fixture()
def first_user_id():
    """Получаем id первого пользователя"""
    first_user = User.objects.order_by('id').first()
    return first_user.id


@pytest.fixture()
def second_authenticated_client():
    """Фикстура второго авторизированного клиента."""
    client = APIClient()
    second_authenticated_data = {
        'email': 'test_user_03@yandex.ru',
        'username': 'test_user_03',
        'first_name': 'Николай',
        'last_name': 'Романов',
        'password': CURRENT_PASSWORD
    }
    client.post(
        USER_URL, second_authenticated_data)
    login_response = client.post(
        URL_GET_LOGIN,
        {
            'email': second_authenticated_data['email'],
            'password': second_authenticated_data['password']
        }
    )
    token = login_response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client, second_authenticated_data


@pytest.fixture()
def second_user_id():
    """Получаем id второго пользователя."""
    second_user = User.objects.latest('id')
    return second_user.id


@pytest.fixture()
def create_ingredients():
    """Создаем ингредиенты в базе данных."""
    ingredients_data = [
        {'name': 'ingredient01', 'measurement_unit': 'measurement_unit01'},
        {'name': 'ingredient02', 'measurement_unit': 'measurement_unit02'},
        {'name': 'other_ingredient', 'measurement_unit': 'measurement_unit03'},
    ]
    for ingredient in ingredients_data:
        Ingredient.objects.get_or_create(**ingredient)


@pytest.fixture()
def create_tags():
    """Создаем тэги в базе данных."""
    tags_data = [
        {"name": "tag01", "slug": "tag01"},
        {"name": "tag02", "slug": "tag02"},
        {"name": "tag03", "slug": "tag03"},
    ]
    for tag in tags_data:
        Tag.objects.get_or_create(**tag)


@pytest.fixture()
def setup_data():
    """Данные для создания рецепта."""
    return {
        'ingredients': [{'id': 1, 'amount': 10}],
        'tags': [1, 2],
        'image': RECIPE_IMAGE,
        'name': 'string01',
        'text': 'string01',
        'cooking_time': 1
    }


@pytest.fixture
def create_recipes(
    create_ingredients, create_tags, setup_data,
    authenticated_client, second_authenticated_client
):
    """Создаем рецепты в базе данных."""
    first_client, first_authenticated_data = authenticated_client
    second_client, second_authenticated_data = second_authenticated_client
    recipes = []

    first_recipe = setup_data.copy()
    first_recipe['name'] = 'first_recipe'
    first_response = first_client.post(
        RECIPE_URL, first_recipe, format=FORMAT
    )
    recipes.append(first_response.data)

    second_recipe = setup_data.copy()
    second_recipe['name'] = 'second_recipe'
    second_recipe['tags'] = [3]
    second_response = second_client.post(
        RECIPE_URL, second_recipe, format=FORMAT
    )
    recipes.append(second_response.data)
    return recipes


@pytest.fixture()
def first_recipe_id():
    """Получаем id первого рецепта."""
    first_recipe = Recipe.objects.order_by('id').first()
    return first_recipe.id


@pytest.fixture()
def second_recipe_id():
    """Получаем id второго рецепта."""
    second_recipe = Recipe.objects.latest('id')
    return second_recipe.id


@pytest.fixture()
def create_favorite(
    create_recipes, second_authenticated_client, first_recipe_id
):
    """Добавляем рецепт в избранное."""
    client, _ = second_authenticated_client
    response = client.post(
        f'{RECIPE_URL}{first_recipe_id}{FAVORITE_URL}'
    )
    return response

@pytest.fixture
def create_shopping_cart(
    second_authenticated_client, create_recipes, first_recipe_id
):
    """Добавляем рецепт в избранное."""
    client, _ = second_authenticated_client
    response = client.post(
        f'{RECIPE_URL}{first_recipe_id}{SHOPPING_CART_URL}'
    )
    return response
