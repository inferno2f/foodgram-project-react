# Generated by Django 3.2.12 on 2022-03-30 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_recipe_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
    ]