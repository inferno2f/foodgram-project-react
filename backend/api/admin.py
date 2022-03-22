from django.contrib import admin

from api import models

admin.site.register(models.Recipe)
admin.site.register(models.Ingredient)
admin.site.register(models.Tag)
admin.site.register(models.RecipeIngredients)
