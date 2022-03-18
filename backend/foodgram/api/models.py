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
    tag = models.ManyToManyField('Tag', verbose_name='Тэг')
    time = models.SmallIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=(
            MinValueValidator(
                1, 'Выберите правильное время приготовления!'),))
    # FIXME: протестировать работу корзины и избранных. Нэйминг может быть лучше
    favorite = models.ManyToManyField(
        CustomUser, verbose_name='Избранные рецепт', related_name='favorite_recipes')
    cart = models.ManyToManyField(
        CustomUser, verbose_name='Корзина', related_name='shopping_cart')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'Рецепт: {self.name} | Автор: {self.author}'


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Ингридиент')
    units = models.CharField(max_length=200, verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'Игредицент {self.name} ({self.units})'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Тэг')
    color_code = models.CharField(max_length=7, unique=True, verbose_name='HEX-код цвета')
    slug = models.SlugField(max_length=200, unique=True, blank=False)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'Тэг {self.name} ({self.color_code})'


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
        return f'{self.ingredient.name} - {self.amount} {self.ingredient.units}'
