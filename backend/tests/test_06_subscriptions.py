import pytest
from tests.constants import USER_URL


@pytest.mark.django_db
class TestSubscriptions:

    SUBSCRIBE_URL = "/subscribe/"
    SUBSCRIPTION_URL = "/api/users/subscriptions/"

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = (
            authenticated_client
        )

    @pytest.fixture(autouse=True)
    def setup_second_authenticated_client(self, second_authenticated_client):
        """
        Вызываем фикстуру второго авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.second_authenticated_client, self.second_authenticated_data = (
            second_authenticated_client
        )

    @pytest.fixture
    def create_01_subscription(self, second_user_id):
        """Создаем подписку на пользователя."""
        response = self.authenticated_client.post(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        return response

    def test_02_subscribe_user(self, second_user_id):
        """Проверяем возможность подписаться на пользователя."""
        response = self.authenticated_client.post(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        assert response.status_code == 201
        assert response.data["username"] == (
            self.second_authenticated_data["username"]
        )
        assert response.data["email"] == (
            self.second_authenticated_data["email"]
        )
        assert response.data["is_subscribed"] is True

    def test_03_not_subscribe_himself(self, first_user_id):
        """Проверяем невозможность подписаться на самого себя."""
        response = self.authenticated_client.post(
            f"{USER_URL}{first_user_id}{self.SUBSCRIBE_URL}"
        )
        assert response.status_code == 400
        assert "errors" in response.data

    def test_04_unauthorized_user_cant_subscribe(self, client, second_user_id):
        """
        Проверяем, что неавторизованный пользователь не может подписаться.
        """
        response = client.post(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        assert response.status_code == 401
        assert "detail" in response.data

    def test_05_subscribe_twice(self, create_subscription, second_user_id):
        """
        Проверяем, что невозможно подписаться дважды
        на одного пользователя.
        """
        response = create_subscription
        assert response.status_code == 201
        second_response = self.authenticated_client.post(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        assert second_response.status_code == 400
        assert "errors" in second_response.data

    def test_06_get_subscriptions(self, create_subscription):
        """Проверяем доступность списка подписок."""
        response = self.authenticated_client.get(self.SUBSCRIPTION_URL)
        assert response.status_code == 200
        assert "results" in response.data

    def test_07_unauthorized_user_cant_get_subscriptions(self, client):
        """
        Проверяем, что неавторизованный пользователь
        не сможет подписаться.
        """
        response = client.get(self.SUBSCRIPTION_URL)
        assert response.status_code == 401
        assert "detail" in response.data

    def test_08_delete_subscribe(self, create_subscription, second_user_id):
        """Проверяем возможность отписаться от пользователя."""
        response = self.authenticated_client.delete(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        assert response.status_code == 204
        assert response.data is None

    def test_09_delete_not_subscriber(self, second_user_id):
        """
        Проверяем, что нельзя отписаться от пользователя
        на которого не был подписан.
        """
        response = self.authenticated_client.delete(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        assert response.status_code == 400
        assert "errors" in response.data

    def test_10_unauthorized_user_cant_delete(self, client, second_user_id):
        """
        Проверяем, что неавторизованный пользователь
        не может отписываться.
        """
        response = client.delete(
            f"{USER_URL}{second_user_id}{self.SUBSCRIBE_URL}"
        )
        assert response.status_code == 401
        assert "detail" in response.data
