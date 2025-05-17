import json

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def handle(self, *args, **options):
        filename = 'data/ingredients.json'

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            new_ingredients = []
            existing = set(
                Ingredient.objects.values_list("name", "measurement_unit")
            )

            for item in data:
                name = item['name'].strip()
                unit = item['measurement_unit'].strip()
                if (name, unit) not in existing:
                    new_ingredients.append(
                        Ingredient(name=name, measurement_unit=unit)
                    )
                    existing.add((name, unit))

            with transaction.atomic():
                Ingredient.objects.bulk_create(new_ingredients)

            self.stdout.write(self.style.SUCCESS(
                f'Импортировано ингредиентов: {len(new_ingredients)}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при импорте из файла {filename}: {str(e)}'
            ))
