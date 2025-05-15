import csv
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'

    def handle(self, *args, **options):
        try:
            if Ingredient.objects.exists():
                self.stdout.write(self.style.WARNING(
                'Ingredients already exist'
            ))
                return
            with open("../data/ingredients.csv", 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                with transaction.atomic():
                    ingrs = [
                        Ingredient(
                            name=name.strip(),
                            measurement_unit=measurement_unit.strip()
                        )
                        for name, measurement_unit in reader
                    ]
                    Ingredient.objects.bulk_create(ingrs)

                    self.stdout.write(self.style.SUCCESS(
                        f'Ingredients were imported'
                    ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при импорте данных: {str(e)}'
            ))