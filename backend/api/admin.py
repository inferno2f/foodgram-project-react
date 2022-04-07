from django.contrib import admin

from api import models


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_recipe_count')
    list_filter = ('tags__name',)
    empty_value_display = '--empty--'

    def favorite_recipe_count(self, obj):
        return obj.favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_filter = ('recipe__author',)

admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Tag)
admin.site.register(models.RecipeIngredient, RecipeIngredientAdmin)
