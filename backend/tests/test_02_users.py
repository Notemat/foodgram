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

    def test_successful_login(self, client, user_data):
        """Проверяем возможность авторизации с корректными данными."""
        self.client.post(self.URL_SIGNUP, user_data)
        response = self.client.post(
            self.URL_GET_LOGIN,
            {'email': user_data['email'], 'password': user_data['password']}
        )
        assert response.status_code == 200
        assert 'auth_token' in response.data

    def test_login_with_invalid_password(self, client, user_data):
        """Проверяем возможность авторизации с некорректными данными."""
        self.client.post(self.URL_SIGNUP, user_data)
        response = self.client.post(
            self.URL_GET_LOGIN,
            {'email': user_data['email'], 'password': self.WRONG_PASSWORD}
        )
        assert response.status_code == 401
        assert 'detail' in response.data

    def test_successful_logout(self, client, user_data):
        """Проверяем возможность удаления токена с корректными данными."""
        self.client.post(self.URL_SIGNUP, user_data)
        login_response = self.client.post(
            self.URL_GET_LOGIN,
            {'email': user_data['email'], 'password': user_data['password']}
        )
        token = login_response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        logout_response = self.client.post(self.URL_GET_LOGOUT)
        assert logout_response.status_code == 204

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        failed_response = self.client.get(self.USER_ME_URL)
        assert failed_response.status_code == 401
