from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from .models import Work, Comment, CcSetting, Favorite, MediaImage, MediaSound
from accounts.serializers import MainInfoSerializer
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField
import six

def file_validator(file):
    max_file_size = 1024 * 1024 * 20  # 1MB

    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is {} and your file size is {}'.
            format(max_file_size, file.size)))
class FileListSerializer(serializers.Serializer):
    media = serializers.ListField(
        child = serializers.FileField( max_length = 100000,
            allow_empty_file=False, use_url=False, validators=[file_validator] )
    )
    choice = serializers.BooleanField()

    def create(self, validated_data):
        media_source = validated_data.pop('media')
        choice = validated_data.pop('choice')
                
        if choice:
            return_array = []
            for img in media_source:
                media_image = MediaImage.objects.create(uri = img)
                return_array.append(media_image.id)
        else:
            return_array = []
            for sound in media_source:
                sound_file = MediaSound.objects.create(uri = sound)
                return_array.append(sound_file.id)           

        return return_array
class CcSettingSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = ('id', 'image', 'en_name', 'cc')
        model = CcSetting

class MediaImageSerializer(serializers.ModelSerializer):
    uri = Base64ImageField()
    class Meta:
        fields = ('uri', 'id')
        model = MediaImage

    def create(self, validated_data):
        image = validated_data.pop('uri')
        curMediaImage = MediaImage.objects.create(**validated_data)
        curMediaImage.image = image
        curMediaImage.save()
        return True

class WorkTagListSerializerField(TagListSerializerField):
    def to_internal_value(self, value):
        if isinstance(value, six.string_types):
            value = value.split(',')

        if not isinstance(value, list):
            self.fail('not_a_list', input_type=type(value).__name__)

        for s in value:
            if not isinstance(s, six.string_types):
                self.fail('not_a_str')

            self.child.run_validation(s)
        return value

class WorkSerializer(serializers.ModelSerializer):
    creator = MainInfoSerializer(read_only=True)
    collaborators = MainInfoSerializer(read_only=True, many=True)
    cc_setting = CcSettingSerializer(read_only=True)
    hearts = serializers.SerializerMethodField(read_only = True)
    tags = WorkTagListSerializerField(read_only=True)
    images = MediaImageSerializer(read_only=True, many=True)
    sounds = MediaImageSerializer(read_only = True, many = True)    
    comments_count = serializers.SerializerMethodField(read_only = True)

    class Meta:
        fields = ('id', 'title', 'creator', 'collaborators', 'tags', 'url', 
            'cc_setting', 'images', 'created_at', 'hearts', 'comments_count',
            'status', 'sounds', 'content', 'updated_at')
        model = Work

    def get_queryset(self):
        return Work.objects.order_by("-created_at").all()

    def get_hearts(self, obj):
        return obj.likers.count()
    
    def get_comments_count(self, obj):
        return obj.comments.filter(commentor__is_active = True).count()

class WorkUploadSerializer(serializers.Serializer):
    medias = serializers.ListField(
        child = serializers.IntegerField(min_value = 1)
    )
    title = serializers.CharField(max_length = 192)
    content = serializers.CharField(allow_blank = True)
    status = serializers.CharField(max_length = 10)
    cc_setting = serializers.IntegerField(min_value = 1)
    collaborators = serializers.ListField(
        child = serializers.IntegerField(min_value = 1)
    )
    url = serializers.CharField(max_length = 255, allow_blank = True, required = False)
    tags = WorkTagListSerializerField()
    choice = serializers.BooleanField()

class WorkPaginationSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value = 0)
    size = serializers.IntegerField(min_value = 3)
    offset = serializers.IntegerField(min_value = 0)
    creator = serializers.IntegerField(min_value = 0)
    q = serializers.CharField(required=False)

class CommentsPaginatorSerializer(serializers.Serializer):
    work = serializers.IntegerField(min_value = 1)
    page = serializers.IntegerField(min_value = 0)
    size = serializers.IntegerField(min_value = 3)
    offset = serializers.IntegerField(min_value = 0)

class CommentSerializer(serializers.ModelSerializer):
    commentor = MainInfoSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        fields = ('commentor', 'parent', 'content')
        model = Comment

        def get_related_field(self, model_field):
            return CommentSerializer()
