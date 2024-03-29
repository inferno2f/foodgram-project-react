# Generated by Django 3.2.12 on 2022-03-16 19:28

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Ингридиент')),
                ('units', models.CharField(max_length=12, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Рецепт')),
                ('image', models.ImageField(upload_to='', verbose_name='Фото')),
                ('description', models.TextField(verbose_name='Описание рецепта')),
                ('time', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Выберите правильное время приготовления!')], verbose_name='Время приготовления (мин)')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='Тэг')),
                ('color_code', models.CharField(max_length=8, verbose_name='HEX-код цвета')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Добавьте необходимое количество для ингредиента')], verbose_name='Количество ингредиента')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Количество ингредиента',
                'verbose_name_plural': 'Количество ингредиентов',
            },
        ),
    ]
