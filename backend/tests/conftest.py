from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, User


@pytest.fixture
def user_data():
    """Фикстура модели с данными тестового пользователя."""
    return {
        'email': 'test_user_01@yandex.ru',
        'username': 'test_user_01',
        'first_name': 'Вася',
        'last_name': 'Иванов',
        'password': 'Qwerty123'
    }


@pytest.fixture
def create_user_01(db, user_data):
    """Фикстура модели обычного пользователя."""
    return User.objects.create_user(
        email='test_user_01@yandex.ru',
        username='test_user_01',
        password='Qwerty123'
    )


@pytest.fixture
def auth_token(client, create_user):
    """Фикстура для получения токена аутентификации."""
    response = client.post(
        '/api/auth/token/login/',
        {"email": "test_user_01@yandex.ru", "password": "Qwerty123"}
    )
    return response.data['auth_token']


@pytest.fixture
def api_client():
    """Фикстура для тестового клиента."""
    return APIClient()


# @pytest.fixture
# def not_author_client(django_user_model):
#     """Логиним обычного пользователя в клиенте."""
#     client = Client()
#     client.force_login(not_author)
#     return client

# @pytest.fixture
# def recipe():
#     """Фикстура модели рецепта."""
#     recipe = Recipe.objects.create(
        
#     )


@pytest.fixture
def author(django_user_model):
    """Фикстура модели пользователя-автора."""
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(django_user_model):
    """Логиним автора в клиенте."""
    client = Client()
    client.force_login(author)
    return client

