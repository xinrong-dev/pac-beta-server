# Generated by Django 3.1.2 on 2020-10-18 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20201017_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='is_registered',
            field=models.BooleanField(default=False, verbose_name='初期登録'),
        ),
    ]
