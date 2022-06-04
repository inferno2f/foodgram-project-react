import csv
import os

from django.core.management.base import BaseCommand

from api.models import Ingredient
from foodgram.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        file = open(os.path.join(BASE_DIR, 'data', 'ingredients.csv'))
        read_file = csv.reader(file)
        count = 1
        for ingredient in read_file:
            if count == 1:
                pass
            else:
                # Specify model and query details here
                Ingredient.objects.get_or_create(
                    name=ingredient[0],
                    measurement_unit=ingredient[1])
            count += 1
