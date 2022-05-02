from django.db import models
from taggit.managers import TaggableManager
from accounts.models import Member
from django.core.files.storage import get_storage_class
from django.core.files.storage import default_storage

# CcSetting


class CcSetting(models.Model):
    def __str__(self):
        return self.cc

    cc = models.CharField('CC', max_length=255)
    en_name = models.CharField('英語名称', max_length=255, null=True)
    image = models.ImageField(
        '画像',
        null=True,
        blank=True,
        upload_to="static/images/cc/")

    def image_container(self):
        from django.utils.html import format_html
        return format_html(
            "<img src={} style = 'max-width: 300px; margin-right: 10px;'/>".format(self.image.url))

    image_container.short_description = "画像"
    image_container.allow_tags = True

    class Meta:
        verbose_name = "クリエイティブコモンズ"
        verbose_name_plural = "クリエイティブコモンズ"

# MediaImage Model


class MediaImage(models.Model):
    def __str__(self):
        return self.uri.url

    uri = models.ImageField(
        'URI',
        upload_to="static/images/media",
        null=True,
        max_length=255)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

# MediaSound Model


class MediaSound(models.Model):
    def __str__(self):
        return self.uri.url

    uri = models.FileField(
        'URI',
        upload_to="static/sounds",
        null=True,
        max_length=255)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

# Create your models here.


class Work(models.Model):
    def __str__(self):
        return self.title

    class WorkType(models.TextChoices):
        DRAFT = 'draft', '下書き'
        PUBLIC = 'public', '公開'
        PRIVATE = 'private', '非公開'

    title = models.CharField('タイトル', max_length=255)
    content = models.TextField('コンテンツ', null=True, blank=True)
    status = models.CharField(
        'ステータス',
        choices=WorkType.choices,
        default=WorkType.DRAFT,
        max_length=10)
    creator = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        verbose_name='作成者',
        related_name="works")
    collaborators = models.ManyToManyField(
        Member, blank=True, verbose_name='コラボレーター', related_name="+")
    url = models.URLField('URL', null=True, blank=True)
    tags = TaggableManager()
    cc_setting = models.ForeignKey(
        CcSetting,
        on_delete=models.PROTECT,
        verbose_name='CC設定')
    images = models.ManyToManyField(
        MediaImage,
        related_name="media",
        verbose_name="画像")
    sounds = models.ManyToManyField(
        MediaSound,
        related_name="sound",
        verbose_name="サウンド")
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def image_container(self):
        from django.utils.html import format_html
        images_string = ""
        for image_item in self.images.all():
            images_string += "<img src={} style = 'max-width: 300px; margin-right: 10px;'/>".format(
                image_item.uri.url)
        html_string = "<div class = 'image-container'>{}<div>".format(
            images_string)
        return format_html(html_string)

    image_container.short_description = "メディア"
    image_container.allow_tags = True

    class Meta:
        verbose_name = "作品"
        verbose_name_plural = "作品"

# Like Model


class Favorite(models.Model):
    def __unicode__(self):
        return self.name()

    liker = models.ForeignKey(
        Member,
        null=True,
        on_delete=models.SET_NULL,
        related_name="favorites",
        verbose_name="ユーザー")
    favorite = models.ForeignKey(
        Work,
        null=True,
        on_delete=models.SET_NULL,
        related_name="likers",
        verbose_name="作品")
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    def name(self):
        return str(self.liker) + "💖" + self.favorite.title + \
            "(" + str(self.favorite.creator) + ")"

    name.short_description = "名称"
    name.tags_allowed = True

    class Meta:
        verbose_name = "イイネ関係"
        verbose_name_plural = "イイネ関係"

# Comment Model


class Comment(models.Model):
    def __str__(self):
        if self.work:
            return str(self.commentor) + " >> " + str(self.work)
        elif self.parent:
            return str(self.commentor) + " >> " + self.parent.content[0:30] if len(
                self.parent.content) > 30 else self.parent.content
        else:
            return "未定"

    work = models.ForeignKey(
        Work,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments",
        verbose_name="作品")
    commentor = models.ForeignKey(
        Member,
        null=True,
        on_delete=models.SET_NULL,
        related_name="my_comments",
        verbose_name="コメンター")
    parent = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name="親コメント")
    content = models.TextField('内容')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
