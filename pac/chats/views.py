from django.shortcuts import render
from .serializers import *
from django.db.models import Q, Count, Case, When, IntegerField, Sum
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, SAFE_METHODS
from rest_framework.response import Response
from .models import Message
from accounts.models import Member
from django.db import connection

# Create your views here.
class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        input_serializer = ChatUserPaginationSerializer(data = request.query_params)
        if input_serializer.is_valid():
            input_data = input_serializer.data
            keyword = ""

            if 'keyword' in input_data.keys():
                keyword = input_data['keyword'].strip()
            page = input_data['page']
            size = input_data['size']
            offset = input_data['offset']
            start_index = page * size + offset

            if keyword == "":
                message_query = Message.objects.filter(
                    Q(Q(receiver__is_active = True) & Q(sender__id = user.id)) | Q(Q(receiver__id = user.id) & Q(sender__is_active = True))
                ).order_by('-created_at')
            else:
                message_query = Message.objects.filter(
                    Q(Q(receiver__user_id__icontains = keyword) & Q(receiver__is_active = True) & Q(sender__id = user.id)) | Q(Q(sender__user_id__icontains = keyword) & Q(receiver__id = user.id) & Q(sender__is_active = True))
                ).order_by('-created_at')

            result = message_query.values('room_str').order_by('room_str', '-created_at').annotate(
                unread = Count('room_str', filter = Q(receiver_id = user.id) & Q(is_read = 0))                
                ).order_by()[start_index:start_index + size]

            result_array = []
            for item in result:
                result_item = {}
                last_message = Message.objects.filter(room_str = item['room_str']).order_by('-created_at').first()
                target_user = last_message.sender if last_message.receiver.id == user.id else last_message.receiver
                result_item['user'] = target_user
                result_item['unread'] = item['unread']
                result_item['message'] = last_message.content
                result_array.append(result_item)
           
            return Response(ChatUserOutputSerializer(result_array, many = True).data, status = status.HTTP_200_OK)
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        input_serializer = MessagePaginationSerializer(data = request.query_params)
        if input_serializer.is_valid():
            input_data = input_serializer.data
            keyword = ""

            target_id = input_data['target_id']
            page = input_data['page']
            size = input_data['size']
            offset = input_data['offset']
            start_index = page * size + offset

            message_query = Message.objects.filter(
                Q(Q(receiver__id = target_id) & Q(sender__id = user.id)) | Q(Q(receiver__id = user.id) & Q(sender__id = target_id))
                ).order_by('-created_at')[start_index:start_index + size]
            return Response(MessageSerializer(message_query, many = True).data, status = status.HTTP_200_OK)

        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        user = request.user

        target_id = request.data['target_id']
        content = request.data['content']
        if int(target_id) > 0 and content.strip() != "":
            target_user = Member.objects.get(pk = int(target_id))
            content = content.strip()

            new_message = Message.objects.create(content = content, sender = request.user, receiver = target_user)
            return Response(MessageSerializer(new_message).data, status = status.HTTP_200_OK)
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reset_message(request, id = None):
    target_id = id
    target_user = Member.objects.get(pk = int(target_id))
    user = request.user

    Message.objects.filter(sender = target_user, receiver = user).update(is_read = 1)
    return Response({"success": True}, status.HTTP_200_OK)

