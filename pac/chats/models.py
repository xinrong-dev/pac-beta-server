from django.db import models
from accounts.models import Member

# Messages


class Message(models.Model):
    def __str__(self):
        return self.content[0:50] if len(self.content) > 50 else self.content

    content = models.TextField("内容")
    image = models.ImageField(
        "画像",
        upload_to="static/images/message",
        max_length=255,
        null=True,
        blank=True)
    sender = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="送信側")
    receiver = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="受信側")
    is_read = models.BooleanField("読んだ", default=False)
    room_str = models.CharField("ルーム", default="", max_length=50)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'メッセージ'
        verbose_name_plural = 'メッセージ'

    def save(self, *args, **kwargs):
        if self.receiver.id < self.sender.id:
            self.room_str = "{0}-{1}".format(self.receiver.id, self.sender.id)
        else:
            self.room_str = "{0}-{1}".format(self.sender.id, self.receiver.id)

        super(Message, self).save(*args, **kwargs)
