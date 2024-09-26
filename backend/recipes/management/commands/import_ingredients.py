import csv
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Импортируем ингредиенты."""

    def handle(self, *args, **kwargs):
        self.import_csv()
        self.import_json()

    def import_csv(self):
        with open(
            'data/ingredients.csv', newline='', encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row['name'], measurement_unit=row['measurement_unit']
                )

    def import_json(self):
        with open('data/ingredients.json', 'r', encoding='utf-8') as jsonfile:
            ingredients = json.load(jsonfile)
            for ingredient in ingredients:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
