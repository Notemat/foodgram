from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, User


URL_SIGNUP = '/api/users/'
URL_GET_LOGIN = '/api/auth/token/login/'
CURRENT_PASSWORD = 'Qwerty321'
RECIPE_URL = '/api/recipes/'
RECIPE_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///"
    "9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByx"
    "OyYQAAAABJRU5ErkJggg=="
)
FORMAT = 'json'
RECIPES_COUNT = 2


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
        URL_SIGNUP, authenticated_data)
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
        URL_SIGNUP, second_authenticated_data)
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


@pytest.fixture
def create_recipes(setup_data, authenticated_client):
    """Создаем рецепты в базе данных."""
    client, authenticated_data = authenticated_client
    recipes = []

    first_recipe = setup_data.copy()
    first_recipe['name'] = 'first_recipe'
    first_response = client.post(
        RECIPE_URL, first_recipe, format=FORMAT
    )
    recipes.append(first_response.data)

    second_recipe = setup_data.copy()
    second_recipe['name'] = 'second_recipe'
    second_response = client.post(
        RECIPE_URL, second_recipe, format=FORMAT
    )
    recipes.append(second_response.data)
    return recipes
