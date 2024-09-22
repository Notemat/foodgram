import pytest

from recipes.models import Tag


@pytest.mark.django_db
class TestTags:

    TAGS_URL = '/api/tags/'

    @pytest.fixture(autouse=True)
    def create_tags(self, create_tags):
        """Вызываем фикстуру ингредиентов."""
        self.tags_data = create_tags

    def test_get_list_tags(self, client):
        """Проверяем доступность списка ингредиентов."""
        tags_count = Tag.objects.count()
        response = client.get(self.TAGS_URL)
        assert response.status_code == 200
        response_count = len(response.data)
        assert response_count == tags_count

    def test_get_tag(self, client, create_tags):
        """Проверяем доступность отдельного ингредиента."""
        tag = Tag.objects.latest('id')
        tag_id = tag.id
        response = client.get(f'{self.TAGS_URL}{tag_id}/')
        assert response.status_code == 200
        assert 'name' in response.data
