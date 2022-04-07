from dataclasses import fields
from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Ингредиент')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Тэг')
    color = models.CharField(
        max_length=7, unique=True, verbose_name='HEX-код цвета')
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes')
    name = models.CharField(max_length=64, verbose_name='Рецепт')
    image = models.ImageField(verbose_name='Фото')
    description = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='api.RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='recipes')
    tags = models.ManyToManyField(
        'Tag', verbose_name='Тэг', default=None, blank=True)
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


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Рецепт')
    amount = models.SmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=(
            MinValueValidator(
                1, 'Добавьте необходимое количество для ингредиента'),))

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_constraint')
        ]

    def __str__(self) -> str:
        return (
            f'{self.recipe.name}: {self.ingredient.name} - '
            f'{self.amount} {self.ingredient.units}'
        )
