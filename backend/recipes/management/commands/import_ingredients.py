import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Импортируем ингредиенты."""

    def handle(self, *args, **kwargs):
        self.import_json()

    def import_json(self):
        with open('data/ingredients.json', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
