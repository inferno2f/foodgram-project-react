# Generated by Django 3.2.12 on 2022-03-27 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписки пользователя', 'verbose_name_plural': 'Подписки пользователей'},
        ),
    ]
