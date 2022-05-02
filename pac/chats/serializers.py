from rest_framework import serializers
from accounts.serializers import MainInfoSerializer
from .models import Message


class ChatUserPaginationSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False)
    page = serializers.IntegerField(min_value=0)
    size = serializers.IntegerField(min_value=3)
    offset = serializers.IntegerField(min_value=0)


class MessagePaginationSerializer(serializers.Serializer):
    target_id = serializers.IntegerField(min_value=1)
    page = serializers.IntegerField(min_value=0)
    size = serializers.IntegerField(min_value=3)
    offset = serializers.IntegerField(min_value=0)


class ChatUserOutputSerializer(serializers.Serializer):
    user = MainInfoSerializer(read_only=True)
    message = serializers.CharField()
    unread = serializers.IntegerField(min_value=0)


class MessageSerializer(serializers.ModelSerializer):
    receiver = MainInfoSerializer(read_only=True)
    sender = MainInfoSerializer(read_only=True)

    class Meta:
        fields = ('id', 'content', 'image', 'sender', 'receiver', 'created_at')
        model = Message
