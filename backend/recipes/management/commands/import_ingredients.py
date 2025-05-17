import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def handle(self, *args, **options):
        filename = 'data/ingredients.json'

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                before_count = Ingredient.objects.count()
                Ingredient.objects.bulk_create([
                    Ingredient(**item) for item in json.load(f)
                ], ignore_conflicts=True)

                self.stdout.write(self.style.SUCCESS(
                    f'Импортировано ингредиентов: {Ingredient.objects.count()
                                                   - before_count}'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при импорте из файла {filename}: {str(e)}'
            ))
