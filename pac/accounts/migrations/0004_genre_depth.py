# Generated by Django 3.1.2 on 2020-10-17 19:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20201017_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='depth',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)], verbose_name='深み'),
        ),
    ]
