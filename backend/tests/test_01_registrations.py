import pytest


@pytest.mark.django_db
class TestUserRegistration:

    URL_SIGNUP = '/api/users/'
    URL_GET_TOKEN = '/api/auth/token/login/'

    @pytest.fixture(autouse=True)
    def user_data(self):
        return {
            'email': 'test_user_01@yandex.ru',
            'username': 'test_user_01',
            'first_name': 'Вася',
            'last_name': 'Иванов',
            'password': 'Qwerty123'
        }

    def test_successful_registration(self, client, user_data):
        """Проверяем, что пользователь может успешно зарегистрироваться."""
        response = client.post(self.URL_SIGNUP, user_data)
        assert response.status_code == 201
        assert 'email' in response.data

    def test_registration_with_existing_email(self, client, user_data):
        """Проверяем, что нельзя зарегистрироваться с существующими данными."""
        client.post(self.URL_SIGNUP, user_data)
        response = client.post(self.URL_SIGNUP, user_data)
        assert response.status_code == 400
        assert 'email' in response.data
        assert 'username' in response.data

    def test_registration_without_password(self, client, user_data):
        """Проверяем, что нельзя зарегистрироваться с незаполненым полем."""
        user_data_without_password = user_data.copy()
        user_data_without_password.pop('password')
        response = client.post(self.URL_SIGNUP, user_data_without_password)
        assert response.status_code == 400
        assert 'password' in response.data

    def test_successful_login(self, client, user_data):
        """Проверяем возможность получить токен."""
        client.post(self.URL_SIGNUP, user_data)
        response = client.post(
            self.URL_GET_TOKEN,
            {'email': user_data['email'], 'password': user_data['password']}
        )
        assert response.status_code == 200
        assert 'auth_token' in response.data
