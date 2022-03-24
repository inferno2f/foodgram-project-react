import csv
import os

from api.models import Ingredient
from foodgram.settings import BASE_DIR

def run():
    file = open(os.path.join(BASE_DIR, 'ingredients.csv'))
    read_file = csv.reader(file)

    count = 1

    for ingredient in read_file:
        if count == 1:
            pass
        else:
            Ingredient.objects.create(name=ingredient[0], units=ingredient[1])
        count += 1
