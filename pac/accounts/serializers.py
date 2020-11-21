from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from .models import Member, Banner, Genre
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField

# initialize firebase admin
from .init_firebase_admin import default_app
from firebase_admin import auth as firebase_auth

class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return {self.field_name: data}

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'username', 'user_id', 'avatar', 'introduction', 'website_url', 'instagram_url', 
            'twitter_url', 'facebook_url', 'genre_str')
        model = Member

class MemberSerializer(serializers.ModelSerializer):
    genre_array = ReadWriteSerializerMethodField()
    avatar = Base64ImageField(required = False)
    class Meta:
        fields = (
            'id', 'firebase_id', 'email', 'username', 'user_id', 'avatar', 'language',
            'social_type', 'is_registered', 'is_active', 'introduction', 'website_url',
            'instagram_url', 'twitter_url', 'facebook_url', 'genre_array', 'genre_str', 'used_amount'
        )
        model = Member

    def get_genre_array(self, instance):
        return instance.genre_array()

    def update(self, instance, validated_data):
        avatar_set = False
        if 'avatar' in validated_data.keys():
            avatar_image = validated_data.pop("avatar")
            avatar_set = True
        
        genre_id_array = validated_data.pop("genre_array")

        instance = super().update(instance, validated_data)
        instance.genres.set(genre_id_array)

        if avatar_set:
            instance.avatar = avatar_image        
        instance.save()
        return instance

class MainInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'username', 'user_id', 'avatar', 'genre_str')
        model = Member

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('link', 'order', 'image')
        model = Banner

    def get_queryset(self):
        return Banner.objects.filter('is_shown', True).order_by("order")

class InitialRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'user_id')
        model = Member

class FriendshipSerializer(serializers.Serializer):
    is_new = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_rank = serializers.BooleanField()
    page = serializers.IntegerField(min_value = 0)
    size = serializers.IntegerField(min_value = 3)
    offset = serializers.IntegerField(min_value = 0)

class GenreSerializer(serializers.ModelSerializer):   
    class Meta:
        fields = ('id', 'name', 'sub_order', 'depth', 'parent')
        model = Genre


class CustomJWTSerializer(JSONWebTokenSerializer):

    def __init__(self, *args, **kwargs):
        super(JSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields['firebase_id'] = serializers.CharField(max_length = 192)
        self.fields['social_type'] = serializers.IntegerField(min_value = 0, max_value = 4)
        self.fields['avatar'] = serializers.CharField(max_length = 192, required=False)
        self.fields['email'] = serializers.CharField(max_length = 192, required=False)
        self.fields['username'] = serializers.CharField(max_length = 192, required=False)

    def get_token(self, object):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(object)
        token = jwt_encode_handler(payload)
        return token 

    def validate(self, attrs):
        
        firebase_id = attrs.get("firebase_id")
        social_type = attrs.get("social_type")

        user = firebase_auth.get_user(firebase_id)
        if user:           
            user_obj = Member.objects.filter(firebase_id = firebase_id).first()

            if user_obj:
                # login
                if user_obj.is_active:
                    user_obj.last_login = timezone.now()
                    user_obj.save()
                    # publish token
                    return {
                        'token': self.get_token(user_obj),
                        'user': MemberSerializer(user_obj).data
                    }                        
                else:
                    # blocked user
                    msg = 'Account is blocked.'
                    raise serializers.ValidationError(msg)
            else:
                # register
                new_user = Member(firebase_id = firebase_id, social_type = social_type)
                if attrs.get('email') != None:
                    new_user.email = attrs.get('email')
                # if attrs.get('avatar') != None:
                #     new_user.avatar = attrs.get('avatar')
                if attrs.get('username') != None:
                    new_user.username = attrs.get('username')
                
                new_user.last_login = timezone.now()
                new_user.save()    

                # publish token
                return {
                    'token': self.get_token(new_user),
                    'user': MemberSerializer(new_user).data
                }
        else:
            msg = 'User is not found in the firebase'
            raise serializers.ValidationError(msg)
