# Generated by Django 3.1.2 on 2020-11-10 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20201102_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='used_amount',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=11, null=True, verbose_name='使用容量'),
        ),
    ]