import pytest
from rest_framework.test import APIClient
from tests.constants import CURRENT_PASSWORD, URL_GET_LOGIN, USER_URL


@pytest.mark.django_db
class TestUser:

    URL_GET_LOGOUT = "/api/auth/token/logout/"
    USER_ME_URL = "/api/users/me/"
    PUT_AVATAR_URL = f"{USER_ME_URL}avatar/"
    CHANGE_PASSWORD_URL = "/api/users/set_password/"
    NEW_PASSWORD = "NewPassword123"
    WRONG_PASSWORD = "WrongPassword321"
    AVATAR_IMAGE = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///"
        "9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByx"
        "OyYQAAAABJRU5ErkJggg=="
    )

    @pytest.fixture(autouse=True)
    def setup_unauthorized(self):
        """
        Фикстура неавторизированного клиента
        и данных для регистрации
        """
        self.client = APIClient()
        self.user_data = {
            "email": "test_user_01@yandex.ru",
            "username": "test_user_01",
            "first_name": "Вася",
            "last_name": "Иванов",
            "password": "Qwerty123",
        }

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = (
            authenticated_client
        )

    def test_successful_login(self):
        """Проверяем возможность авторизации с корректными данными."""
        self.client.post(USER_URL, self.user_data)
        response = self.client.post(
            URL_GET_LOGIN,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            },
        )
        assert response.status_code == 200
        assert "auth_token" in response.data

    def test_01_login_with_invalid_password(self):
        """Проверяем возможность авторизации с некорректными данными."""
        self.client.post(USER_URL, self.user_data)
        response = self.client.post(
            URL_GET_LOGIN,
            {
                "email": self.user_data["email"],
                "password": self.WRONG_PASSWORD
            },
        )
        assert response.status_code == 401
        assert "detail" in response.data

    def test_02_successful_logout(self):
        """Проверяем возможность удаления токена с корректными данными."""
        logout_response = self.authenticated_client.post(self.URL_GET_LOGOUT)
        assert logout_response.status_code == 204

        failed_response = self.client.get(self.USER_ME_URL)
        assert failed_response.status_code == 401

    def test_03_get_user_profile(self):
        """Проверяем возможность получения информации о пользователе."""
        register_response = self.client.post(USER_URL, self.user_data)
        user_id = register_response.data["id"]
        response = self.client.get(f"{USER_URL}{user_id}/")
        assert response.status_code == 200
        assert response.data["username"] == self.user_data["username"]
        assert response.data["email"] == self.user_data["email"]

    def test_04_get_me_profile(self):
        """Проверяем возможность получения информации о своем профиле."""
        response = self.authenticated_client.get(self.USER_ME_URL)
        assert response.status_code == 200
        assert response.data["username"] == self.authenticated_data["username"]
        assert response.data["email"] == self.authenticated_data["email"]

    def test_05_not_authenticated_get_me_profile(self):
        """
        Проверяем, что неавторизованный пользователь
        не сможет получить доступ к своему профилю.
        """
        self.client.post(USER_URL, self.user_data)
        response = self.client.get(self.USER_ME_URL)
        assert response.status_code == 401

    def test_06_update_password(self):
        """ "Проверяем возможность изменения пароля пользователя."""
        response = self.authenticated_client.post(
            self.CHANGE_PASSWORD_URL,
            {
                "new_password": self.NEW_PASSWORD,
                "current_password": CURRENT_PASSWORD
            },
        )
        assert response.status_code == 204

    def test_07_not_authenticated_cant_update_password(self):
        """
        Проверяем, что неавторизированный пользователь
        не сможет сменить пароль другого пользователя.
        """
        response = self.client.post(
            self.CHANGE_PASSWORD_URL,
            {
                "new_password": self.NEW_PASSWORD,
                "current_password": CURRENT_PASSWORD
            },
        )
        assert response.status_code == 401

    def test_08_add_avatar(self):
        """Проверяем возможность добавления аватара."""
        response = self.authenticated_client.put(
            self.PUT_AVATAR_URL, {"avatar": self.AVATAR_IMAGE}
        )
        assert response.status_code == 200

    def test_09_not_authenticated_cant_add_avatar(self):
        """
        Проверяем, что неавторизированный пользователь
        не сможет добавить аватар.
        """
        response = self.client.put(self.PUT_AVATAR_URL, {
            "avatar": self.AVATAR_IMAGE
        })
        assert response.status_code == 401

    def test_10_delete_avatar(self):
        """Проверяем возможность удаления аватара."""
        response = self.authenticated_client.delete(
            self.PUT_AVATAR_URL,
        )
        assert response.status_code == 204
        assert "message" in response.data

    def test_11_not_authenticated_cant_delete_avatar(self):
        """
        Проверяем, что неавторизованный пользователь
        не может удалять аватар.
        """
        response = self.client.delete(
            self.PUT_AVATAR_URL,
        )
        assert response.status_code == 401
