from django.shortcuts import render
from django.conf import settings
from rest_framework import status, generics, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.views import JSONWebTokenAPIView
from .serializers import *
from .models import Work, CcSetting, Favorite, Comment
from rest_framework.response import Response
from taggit.models import Tag
# Create your views here.


class SuperUserOnlyPermission(BasePermission):
    message = "Only Superuser is allowed to update info"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user
        else:
            # Check permissions for write request
            return request.user.is_superuser


class IsOwnerPermission(BasePermission):
    message = "Only owner can edit his work"

    def has_object_permission(self, request, view, obj):
        return obj.creator.id == request.user.id


class UploadGallery(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request):
        user = request.user
        if user.used_amount / 1024 / 1024 >= settings.CLIENT_MAX_UPLOAD_SIZE:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if 'amount' in request.data.keys():
            amount = int(request.data['amount'])
            user.used_amount += amount
            user.save()

            serializer = FileListSerializer(data=request.data)
            if serializer.is_valid():
                return_array = serializer.save()
                return Response(return_array, status=status.HTTP_200_OK)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def like_work(request, id=None):
    work_id = id
    cur_work = Work.objects.get(pk=work_id)
    user = request.user
    if user.id == cur_work.creator.id:
        return Response(
            "You can not like your work",
            status.HTTP_400_BAD_REQUEST)
    else:
        cur_count = Favorite.objects.filter(
            liker=user, favorite=cur_work).count()
        if cur_count > 0:
            Favorite.objects.filter(liker=user, favorite=cur_work).delete()
            return Response(
                {"success": True, "result": "minus"}, status.HTTP_200_OK)
        else:
            Favorite.objects.create(liker=user, favorite=cur_work)
            return Response(
                {"success": True, "result": "plus"}, status.HTTP_200_OK)


class WorksDetail(APIView):
    def get_permissions(self):
        if self.request.method == "PUT" or self.request.method == "DELETE":
            self.permission_classes = [
                SuperUserOnlyPermission | IsOwnerPermission]
        else:
            self.permission_classes = [IsAuthenticated]

        return super(WorksDetail, self).get_permissions()

    def get_object(self, pk):
        try:
            return Work.objects.get(pk=pk)
        except Work.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        cur_work = self.get_object(pk)
        serializer = WorkSerializer(cur_work)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        cur_work = self.get_object(pk)
        serializer = WorkUploadSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            medias = []
            cc_setting = 1
            collaborators = []
            url = ""

            if 'medias' in validated_data.keys():
                medias = validated_data.pop('medias')

            if 'collaborators' in validated_data.keys():
                collaborators = validated_data.pop('collaborators')

            if 'cc_setting' in validated_data.keys():
                cc_setting = validated_data.pop('cc_setting')

            if 'tags' in request.data:
                cur_work.tags.set(*request.data['tags'])

            if 'url' in validated_data.keys():
                url = validated_data.get('url')

            choice = validated_data.pop('choice')

            for attr, value in validated_data.items():
                setattr(cur_work, attr, value)

            cur_work.creator = request.user
            cur_work.cc_setting = CcSetting.objects.get(pk=cc_setting)
            cur_work.save()

            if url == "":
                if choice:
                    cur_work.sounds.clear()
                    cur_work.images.set(medias)
                else:
                    cur_work.images.clear()
                    cur_work.sounds.set(medias)
            else:
                cur_work.sounds.clear()
                cur_work.images.clear()

            cur_work.collaborators.set(collaborators)

            return Response(
                WorkSerializer(cur_work).data,
                status=status.HTTP_200_OK)
        else:
            # print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class WorksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = WorkPaginationSerializer(data=request.query_params)
        if serializer.is_valid():
            get_param = serializer.data
            keyword = ""
            if 'q' in get_param.keys():
                keyword = get_param['q']
            creator = get_param['creator']
            page = get_param['page']
            size = get_param['size']
            offset = get_param['offset']
            start_index = page * size + offset

            if creator > 0:
                if creator == user.id:
                    work_queryset = Work.objects.filter(creator__id=creator)
                else:
                    work_queryset = Work.objects.filter(
                        status="public", creator__id=creator)
            else:
                followers_id = list(
                    user.following.filter(
                        followee__is_active=True).values_list(
                        'followee_id', flat=True))
                followers_id.append(user.id)
                work_queryset = Work.objects.filter(
                    status="public", creator__id__in=followers_id)

            if keyword:
                work_queryset = work_queryset.filter(title__icontains="keyword").order_by(
                    "-created_at").all()[start_index:start_index + size]
            else:
                work_queryset = work_queryset.order_by(
                    '-created_at').all()[start_index:start_index + size]

            work_serializer = WorkSerializer(work_queryset, many=True)
            return Response(work_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = WorkUploadSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            medias = []
            cc_setting = 1
            collaborators = []
            url = ""
            if 'medias' in validated_data.keys():
                medias = validated_data.pop('medias')

            if 'collaborators' in validated_data.keys():
                collaborators = validated_data.pop('collaborators')

            if 'cc_setting' in validated_data.keys():
                cc_setting = validated_data.pop('cc_setting')

            if 'url' in validated_data.keys():
                url = validated_data.get('url')

            choice = validated_data.pop('choice')

            new_work = Work(**validated_data)
            new_work.creator = request.user
            new_work.cc_setting = CcSetting.objects.get(pk=cc_setting)
            new_work.save()

            cur_work = Work.objects.get(pk=new_work.id)

            if 'tags' in request.data:
                cur_work.tags.set(*request.data['tags'])

            if url == "":
                if choice:
                    cur_work.images.set(medias)
                else:
                    cur_work.sounds.set(medias)

            cur_work.collaborators.set(collaborators)
            cur_work.save()

            return Response(
                WorkSerializer(cur_work).data,
                status=status.HTTP_200_OK)
        else:
            # print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CcSettingView(generics.ListAPIView):
    queryset = CcSetting.objects.all()
    serializer_class = CcSettingSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_work_comment(request):

    serializer = CommentsPaginatorSerializer(data=request.query_params)
    if serializer.is_valid():
        get_param = serializer.data
        work_id = get_param['work']
        page = get_param['page']
        size = get_param['size']
        offset = get_param['offset']
        start_index = page * size + offset

        work_obj = Work.objects.get(pk=work_id)
        comment_queryset = work_obj.comments.filter(commentor__is_active=True).order_by(
            '-created_at').all()[start_index:start_index + size]

        return Response(
            CommentSerializer(
                comment_queryset,
                many=True).data,
            status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_related_tags(request):
    query = request.GET.get('q', '')
    if query != "":
        tags = Tag.objects.filter(
            name__contains=query).values_list(
            'name', flat=True)
        return Response(tags, status=status.HTTP_200_OK)
    else:
        return Response([], status=status.HTTP_200_OK)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        work_id = request.data['id']
        work_comment = request.data['content']
        user = request.user

        try:
            cur_work = Work.objects.get(pk=work_id)
        except Work.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        Comment.objects.create(
            work=cur_work,
            commentor=user,
            content=work_comment)

        return Response({"success": True}, status.HTTP_200_OK)
