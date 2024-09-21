import pytest

from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUser:

    URL_SIGNUP = '/api/users/'
    URL_GET_LOGIN = '/api/auth/token/login/'
    URL_GET_LOGOUT = '/api/auth/token/logout/'
    USER_ME_URL = '/api/users/me/'
    WRONG_PASSWORD = 'WrongPassword321'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test_user_01@yandex.ru',
            'username': 'test_user_01',
            'first_name': 'Вася',
            'last_name': 'Иванов',
            'password': 'Qwerty123'
        }

    @pytest.fixture(autouse=True)
    def authenticated_client(self):
        self.client = APIClient()
        self.authenticated_data = {
            'email': 'test_user_02@yandex.ru',
            'username': 'test_user_02',
            'first_name': 'Иван',
            'last_name': 'Васильев',
            'password': 'Qwerty321'
        }
        self.client.post(
            self.URL_SIGNUP, self.authenticated_data)
        login_response = self.client.post(
            self.URL_GET_LOGIN,
            {
                'email': self.authenticated_data['email'],
                'password': self.authenticated_data['password']
            }
        )
        token = login_response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        return self.client

    def test_successful_login(self):
        """Проверяем возможность авторизации с корректными данными."""
        response = self.client.post(
            self.URL_GET_LOGIN,
            {
                'email': self.user_data['email'],
                'password': self.user_data['password']
            }
        )
        assert response.status_code == 200
        assert 'auth_token' in response.data

    def test_login_with_invalid_password(self):
        """Проверяем возможность авторизации с некорректными данными."""
        response = self.client.post(
            self.URL_GET_LOGIN,
            {'email': self.user_data['email'], 'password': self.WRONG_PASSWORD}
        )
        assert response.status_code == 401
        assert 'detail' in response.data

    def test_successful_logout(self, authenticated_client):
        """Проверяем возможность удаления токена с корректными данными."""
        logout_response = authenticated_client.post(self.URL_GET_LOGOUT)
        assert logout_response.status_code == 204

        failed_response = self.client.get(self.USER_ME_URL)
        assert failed_response.status_code == 401

    def test_get_user_profile(self):
        """Проверяем возможность получения информации о пользователе. """
        register_response = self.client.post(self.URL_SIGNUP, self.user_data)
        user_id = register_response.data['id']
        response = self.client.get(f'{self.URL_SIGNUP}{user_id}/')
        assert response.status_code == 200
        assert response.data['username'] == self.user_data['username']
        assert response.data['email'] == self.user_data['email']

    def test_get_me_profile(self, authenticated_client):
        """Проверяем возможность получения информации о своем профиле. """
        response = authenticated_client.get(self.USER_ME_URL)
        assert response.status_code == 200
        assert response.data['username'] == self.authenticated_data['username']
        assert response.data['email'] == self.authenticated_data['email']

    def test_not_authenticated_get_me_profile(self):
        """
        Проверяем получение информации о своем профиле
        неавторизированным пользователем.
        """
        response = self.client.get(self.USER_ME_URL)
        assert response.status_code == 401
