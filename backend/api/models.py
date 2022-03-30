from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipe')
    name = models.CharField(max_length=64, verbose_name='Рецепт')
    image = models.ImageField(verbose_name='Фото')
    description = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        to='Ingredient',
        through='RecipeIngredients',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField('Tag', verbose_name='Тэг', default=None, blank=True)
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=(
            MinValueValidator(
                1, 'Выберите правильное время приготовления!'),))
    favorite = models.ManyToManyField(
        CustomUser, verbose_name='В избранном', related_name='favorites',
        blank=True)
    cart = models.ManyToManyField(
        CustomUser, verbose_name='В корзине', related_name='shopping_cart',
        blank=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'Рецепт: {self.name} | Автор: {self.author}'


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Ингридиент')
    measurement_unit = models.CharField(max_length=200, verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name} ({self.units})'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Тэг')
    color = models.CharField(
        max_length=7, unique=True, verbose_name='HEX-код цвета')
    slug = models.SlugField(max_length=200, unique=True, blank=False)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'{self.name}'


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    amount = models.SmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=(
            MinValueValidator(
                1, 'Добавьте необходимое количество для ингредиента'),))

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self) -> str:
        return f'{self.recipe.name}: {self.ingredient.name} - {self.amount} {self.ingredient.units}'
