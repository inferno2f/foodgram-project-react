import csv
import os

from api.models import Ingredient
from foodgram.settings import BASE_DIR


# Basic scipt to load data to the db
def run():
    # Specify path to file with fixtures here
    file = open(os.path.join(BASE_DIR, 'ingredients.csv'))
    read_file = csv.reader(file)

    count = 1

    for ingredient in read_file:
        if count == 1:
            pass
        else:
            # Specify model and query details here
            Ingredient.objects.create(
                name=ingredient[0],
                measurement_unit=ingredient[1])
        count += 1
