import pytest

from tests.constants import USER_URL


@pytest.mark.django_db
class TestUserRegistration:

    @pytest.fixture(autouse=True)
    def user_data(self):
        return {
            'email': 'test_user_01@yandex.ru',
            'username': 'test_user_01',
            'first_name': 'Вася',
            'last_name': 'Иванов',
            'password': 'Qwerty123'
        }

    def test_01_successful_registration(self, client, user_data):
        """Проверяем, что пользователь может успешно зарегистрироваться."""
        response = client.post(USER_URL, user_data)
        assert response.status_code == 201
        assert 'email' in response.data

    def test_02_registration_with_existing_email(self, client, user_data):
        """Проверяем, что нельзя зарегистрироваться с существующими данными."""
        client.post(USER_URL, user_data)
        response = client.post(USER_URL, user_data)
        assert response.status_code == 400
        assert 'email' in response.data
        assert 'username' in response.data

    def test_03_registration_without_field(self, client, user_data):
        """Проверяем, что нельзя зарегистрироваться с незаполненым полем."""
        required_fields = [
            'email', 'password', 'first_name', 'last_name', 'username'
        ]
        for field in required_fields:
            data = user_data.copy()
            data.pop(field)
            response = client.post(USER_URL, data)
            assert response.status_code == 400
            assert 'Обязательное поле.' in str(response.data[field][0])
