# Generated by Django 3.1.2 on 2020-10-29 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='image',
            field=models.ImageField(max_length=255, upload_to='static/images/message', verbose_name='画像'),
        ),
    ]