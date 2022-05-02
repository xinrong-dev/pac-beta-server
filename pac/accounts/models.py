from django.db import models
from django.contrib.auth.models import AbstractUser

# django password reset
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django_resized import ResizedImageField

# Genre model


class Genre(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField('カテゴリ', max_length=192)
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='親カテゴリ',
        related_name='children')
    sub_order = models.IntegerField(
        'Sub順序', default=0, validators=[
            MaxValueValidator(5), MinValueValidator(0)])
    order = models.CharField('順序符号', default="0", max_length=255)
    depth = models.IntegerField(
        '深み', default=0, validators=[
            MaxValueValidator(5), MinValueValidator(0)])
    is_shown = models.BooleanField('表示する', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def save(self, *args, **kwargs):
        if self.parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1
            self.order = self.parent.order + "-" + \
                str(self.sub_order) + "-" + self.order
        super(Genre, self).save(*args, **kwargs)

    def is_terminal(self):
        return Genre.objects.filter(parent=self).count() == 0

    class Meta:
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"
# Member model


class Member(AbstractUser):
    def __str__(self):
        return self.user_id if self.user_id else "未定"

    SOCIAL_CHOICES = (
        (0, 'email'),
        (1, 'google'),
        (2, 'facebook'),
        (3, 'twitter')
    )

    class LanguageTypes(models.TextChoices):
        JAPANESE = 'ja', '日本語'
        ENGLISH = 'en', '英語'
        CHINESE = 'zh', '中国語'

    # initial information
    email = models.EmailField(
        'メールアドレス',
        unique=True,
        null=True,
        blank=True,
        max_length=100)
    firebase_id = models.CharField(
        'FirebaseID',
        unique=True,
        null=True,
        blank=True,
        max_length=100)
    social_type = models.IntegerField(
        'ソーシャルタイプ', choices=SOCIAL_CHOICES, default=0)
    username = models.CharField('名前', null=True, blank=True, max_length=192)
    user_id = models.CharField(
        'ユーザーID',
        unique=True,
        null=True,
        blank=True,
        max_length=128)
    avatar = ResizedImageField(
        'アバタ',
        size=[
            300,
            300],
        crop=[
            'middle',
            'center'],
        null=True,
        blank=True,
        upload_to="static/images/avatar",
        quality=75)
    language = models.CharField(
        '言語',
        choices=LanguageTypes.choices,
        default=LanguageTypes.JAPANESE,
        max_length=2)
    introduction = models.TextField('プロファイル', null=True, blank=True)
    is_registered = models.BooleanField('初期登録', default=False)
    used_amount = models.IntegerField('使用容量', default=0)

    # site url
    website_url = models.CharField(
        'サイトURL', null=True, blank=True, max_length=192)
    twitter_url = models.CharField(
        'Twitterリンク',
        null=True,
        blank=True,
        max_length=192)
    instagram_url = models.CharField(
        'Instagramリンク',
        null=True,
        blank=True,
        max_length=192)
    facebook_url = models.CharField(
        'Facebookリンク',
        null=True,
        blank=True,
        max_length=192)

    # category
    genres = models.ManyToManyField(Genre, verbose_name='ジャンル', blank=True)
    genre_str = models.CharField(
        'ジャンル表示',
        null=True,
        blank=True,
        max_length=192)

    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    USERNAME_FIELD = 'firebase_id'
    REQUIRED_FIELDS = ['username', 'email', 'user_id']

    def genre_array(self):
        return self.genres.filter(is_shown=True).values_list('id', flat=True)

    def followers_count(self):
        return self.followers.count()

    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

# Friendships between users


class Friendship(models.Model):
    def __str__(self):
        return self.name()

    follower = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="フォロー元")
    followee = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name="フォロー先")
    created_at = models.DateTimeField(auto_now_add=True)

    def name(self):
        return "{} >> {}".format(str(self.follower), str(self.followee))

    name.short_description = "関係"
    name.allow_tags = True

    class Meta:
        verbose_name = 'フォロー関係'
        verbose_name_plural = 'フォロー関係'
        unique_together = ('follower', 'followee')

    # Friendship.objects.create(follower = user.id, follower = follow.id)
    # user.following.all(), user.followers.all()


# Blockships between users
class Blockship(models.Model):
    def __str__(self):
        return self.name()

    blocker = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='blocked',
        verbose_name="ブロック元")
    blocked = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='blocker',
        verbose_name="ブロック先")
    created_at = models.DateTimeField(auto_now_add=True)

    def name(self):
        return "{} x {}".format(str(self.blocker), str(self.blocked))

    name.short_description = "関係"
    name.allow_tags = True

    class Meta:
        verbose_name = 'ブロック関係'
        verbose_name_plural = 'ブロック関係'
        unique_together = ('blocker', 'blocked')

# Banners


class Banner(models.Model):
    def __str__(self):
        return self.link if self.link else "未定"

    link = models.CharField("リンク", null=True, blank=True, max_length=255)
    image = models.ImageField(
        "画像",
        upload_to="static/images/avatar",
        max_length=255)
    order = models.IntegerField("順序", default=0, validators=[
        MaxValueValidator(10),
        MinValueValidator(0)
    ])
    is_shown = models.BooleanField('表示', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def get_image(self):
        from django.utils.html import format_html
        return format_html(
            "<img src = '{}' style = 'width: 300px;'/>".format(self.image.url))

    get_image.short_description = "画像"
    get_image.allow_tags = True

    class Meta:
        verbose_name = 'フォロー関係'
        verbose_name_plural = 'フォロー関係'
