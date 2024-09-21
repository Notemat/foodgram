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


# @pytest.fixture()
# def second_authenticated_client():
#     """Фикстура второго авторизированного клиента."""
#     client = APIClient()
#     second_authenticated_data = {
#         'email': 'test_user_03@yandex.ru',
#         'username': 'test_user_03',
#         'first_name': 'Николай',
#         'last_name': 'Романов',
#         'password': CURRENT_PASSWORD
#     }
#     client.post(
#         URL_SIGNUP, second_authenticated_data)
#     login_response = client.post(
#         URL_GET_LOGIN,
#         {
#             'email': second_authenticated_data['email'],
#             'password': second_authenticated_data['password']
#         }
#     )
#     token = login_response.data['auth_token']
#     client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
#     return client
