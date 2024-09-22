import pytest

from users.models import User


@pytest.mark.django_db
class TestSubscriptions:

    USERS_URL = '/api/users/'
    SUBSCRIBE_URL = '/subscribe/'
    SUBSCRIPTION_URL = '/api/users/subscriptions/'

    @pytest.fixture(autouse=True)
    def setup_authenticated_client(self, authenticated_client):
        """
        Вызываем фикстуру авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.authenticated_client, self.authenticated_data = \
            authenticated_client

    @pytest.fixture(autouse=True)
    def setup_second_authenticated_client(self, second_authenticated_client):
        """
        Вызываем фикстуру второго авторизованного клиента.

        Сохраняем значения как атрибуты.
        """
        self.second_authenticated_client, self.second_authenticated_data = \
            second_authenticated_client

    @pytest.fixture
    def create_subscription(self):
        """Создаем подписку на пользователя."""
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = self.authenticated_client.post(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        return response

    def test_subscribe_user(self):
        """Проверяем возможность подписаться на пользователя."""
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = self.authenticated_client.post(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        assert response.status_code == 201
        assert response.data['username'] == (
            self.second_authenticated_data['username']
        )
        assert response.data['email'] == (
            self.second_authenticated_data['email']
        )
        assert response.data['is_subscribed'] is True

    def test_not_subscribe_himself(self):
        """Проверяем невозможность подписаться на самого себя."""
        subscriber = User.objects.order_by('id').first()
        subscriber_id = subscriber.id
        response = self.authenticated_client.post(
            f'{self.USERS_URL}{subscriber_id}{self.SUBSCRIBE_URL}'
        )
        assert response.status_code == 400
        assert 'errors' in response.data

    def test_unauthorized_user_cant_subscribe(self, client):
        """
        Проверяем, что неавторизованный пользователь не может подписаться.
        """
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = client.post(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        assert response.status_code == 401
        assert 'detail' in response.data

    def test_subscribe_twice(self, create_subscription):
        """
        Проверяем, что невозможно подписаться дважды
        на одного пользователя.
        """
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = create_subscription
        assert response.status_code == 201
        second_response = self.authenticated_client.post(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        assert second_response.status_code == 400
        assert 'errors' in second_response.data

    def test_get_subscriptions(self, create_subscription):
        """Проверяем доступность списка подписок."""
        response = self.authenticated_client.get(self.SUBSCRIPTION_URL)
        assert response.status_code == 200
        assert 'results' in response.data

    def test_unauthorized_user_cant_get_subscriptions(self, client):
        """
        Проверяем, что неавторизованный пользователь
        не сможет подписаться.
        """
        response = client.get(self.SUBSCRIPTION_URL)
        assert response.status_code == 401
        assert 'detail' in response.data

    def test_delete_subscribe(self, create_subscription):
        """Проверяем возможность отписаться от пользователя."""
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = self.authenticated_client.delete(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        assert response.status_code == 204
        assert response.data is None

    def test_delete_not_subscriber(self):
        """
        Проверяем, что нельзя отписаться от пользователя
        на которого не был подписан.
        """
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = self.authenticated_client.delete(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        assert response.status_code == 400
        assert 'errors' in response.data

    def test_unauthorized_user_cant_delete(self, client):
        """
        Проверяем, что неавторизованный пользователь
        не может отписываться.
        """
        subscribe = User.objects.latest('id')
        subscribe_id = subscribe.id
        response = client.delete(
            f'{self.USERS_URL}{subscribe_id}{self.SUBSCRIBE_URL}'
        )
        assert response.status_code == 401
        assert 'detail' in response.data
