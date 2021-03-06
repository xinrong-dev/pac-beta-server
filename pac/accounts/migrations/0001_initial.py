# Generated by Django 3.1.2 on 2020-10-17 16:03

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=255, verbose_name='リンク')),
                ('image', models.ImageField(max_length='255', upload_to='static/images/avatar', verbose_name='画像')),
                ('order', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)], verbose_name='順序')),
                ('is_shown', models.BooleanField(default=True, verbose_name='表示')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'フォロー関係',
                'verbose_name_plural': 'フォロー関係',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=192, verbose_name='カテゴリ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('parent', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='accounts.genre', verbose_name='親カテゴリ')),
            ],
            options={
                'verbose_name': 'カテゴリ',
                'verbose_name_plural': 'カテゴリ',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=100, null=True, unique=True, verbose_name='メールアドレス')),
                ('firebase_id', models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='FirebaseID')),
                ('social_type', models.IntegerField(choices=[(0, 'email'), (1, 'google'), (2, 'facebook'), (3, 'twitter')], default=0, verbose_name='ソーシャルタイプ')),
                ('username', models.CharField(blank=True, max_length=192, null=True, verbose_name='名前')),
                ('user_id', models.CharField(blank=True, max_length=128, null=True, unique=True, verbose_name='ユーザーID')),
                ('avatar', models.ImageField(blank=True, max_length=192, null=True, upload_to='static/images/avatar', verbose_name='アバタ')),
                ('language', models.CharField(choices=[('ja', '日本語'), ('en', '英語'), ('zh', '中国語')], default='ja', max_length=2, verbose_name='言語')),
                ('introduction', models.TextField(blank=True, null=True, verbose_name='プロファイル')),
                ('website_url', models.CharField(blank=True, max_length=192, null=True, verbose_name='サイトURL')),
                ('twitter_url', models.CharField(blank=True, max_length=192, null=True, verbose_name='Twitterリンク')),
                ('instagram_url', models.CharField(blank=True, max_length=192, null=True, verbose_name='Instagramリンク')),
                ('facebook_url', models.CharField(blank=True, max_length=192, null=True, verbose_name='Facebookリンク')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('genres', models.ManyToManyField(blank=True, to='accounts.Genre', verbose_name='ジャンル')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'ユーザー',
                'verbose_name_plural': 'ユーザー',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('followee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='フォロー先')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='フォロー元')),
            ],
            options={
                'verbose_name': 'フォロー関係',
                'verbose_name_plural': 'フォロー関係',
                'unique_together': {('follower', 'followee')},
            },
        ),
        migrations.CreateModel(
            name='Blockship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocker', to=settings.AUTH_USER_MODEL, verbose_name='ブロック先')),
                ('blocker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked', to=settings.AUTH_USER_MODEL, verbose_name='ブロック元')),
            ],
            options={
                'verbose_name': 'ブロック関係',
                'verbose_name_plural': 'ブロック関係',
                'unique_together': {('blocker', 'blocked')},
            },
        ),
    ]
