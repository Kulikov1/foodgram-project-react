import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader)
        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
        with open(
            f'{data_path}/data/tags.csv',
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Tag.objects.bulk_create(
                Tag(**data) for data in reader)
        self.stdout.write(self.style.SUCCESS('Все теги загружены!'))
