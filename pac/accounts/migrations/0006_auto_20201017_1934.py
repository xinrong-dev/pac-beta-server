# Generated by Django 3.1.2 on 2020-10-17 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_genre_sub_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='order',
            field=models.CharField(default='0', max_length=255, verbose_name='順序符号'),
        ),
    ]
