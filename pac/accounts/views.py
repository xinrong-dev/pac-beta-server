from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import Member, Friendship
from .serializers import *
from rest_framework import status, generics
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.views import JSONWebTokenAPIView
from .init_firebase_admin import default_app

# get user info


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    cur_user = request.user
    serializer = MemberSerializer(cur_user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetail(generics.RetrieveAPIView):
    queryset = Member.objects.all()
    serializer_class = UserDetailSerializer


class MainInfo(generics.RetrieveAPIView):
    queryset = Member.objects.all()
    serializer_class = MainInfoSerializer


class LoginUserView(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's email and password.
    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = CustomJWTSerializer


class InitRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        curUser = request.user

        serializer = InitialRegisterSerializer(
            curUser, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            curUser.is_registered = True
            curUser.save()
            return Response({"success": True, "msg": "ok"},
                            status=status.HTTP_200_OK)
        else:
            if "user_id" in serializer.errors.keys():
                return Response({"success": False,
                                 "msg": serializer.errors["user_id"][0]},
                                status=status.HTTP_200_OK)
            elif "username" in serializer.errors.keys():
                return Response({"success": False,
                                 "msg": serializer.errors["username"][0]},
                                status=status.HTTP_200_OK)


class UserView(generics.ListAPIView):
    queryset = Member.objects.all()
    serializer_class = MainInfoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        real_request = request._request
        queryParams = request.query_params
        keyword = queryParams.get('q')

        page = int(queryParams['page'])
        size = int(queryParams['size'])
        offset = int(queryParams['offset'])
        start_index = page * size + offset
        memberObj = Member.objects.exclude(pk=user.id)

        if keyword:
            member_objects = memberObj.filter(is_active=True, is_registered=True).filter(
                Q(user_id__icontains=keyword) | Q(username__icontains=keyword))
        else:
            member_objects = memberObj.filter(
                is_active=True, is_registered=True)

        memberQuery = member_objects.all()[start_index:start_index + size]
        return Response(
            MainInfoSerializer(
                memberQuery,
                many=True).data,
            status=status.HTTP_200_OK)


class BannerView(generics.ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]


class GenreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        genre_data = []
        for top_genre in Genre.objects.filter(depth=0).order_by('order'):
            genre_data.append(get_tree_list(top_genre))

        return Response(genre_data, status=status.HTTP_200_OK)


def get_tree_list(cur_genre):
    genre_data = GenreSerializer(cur_genre).data
    genre_data["children"] = []
    if cur_genre.is_terminal():
        return genre_data
    else:
        for child_user in Genre.objects.filter(
                parent=cur_genre).order_by('order'):
            genre_data["children"].append(get_tree_list(child_user))

        return genre_data

# get friendship users


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_friendship_user(request):
    cur_user = request.user
    serializer = FriendshipSerializer(data=request.query_params)
    if serializer.is_valid():
        get_param = serializer.data
        is_new = get_param['is_new']
        is_active = get_param['is_active']
        is_rank = get_param['is_rank']
        page = get_param['page']
        size = get_param['size']
        offset = get_param['offset']
        start_index = page * size + offset
        if is_rank:
            members = sorted(
                Member.objects.filter(
                    is_active=True,
                    is_superuser=False),
                key=lambda a: a.followers_count(),
                reverse=True)[start_index:start_index + size]
            returned_user = [item.id for item in members]
            # print(returned_user)
        else:
            if is_active:
                friendships = cur_user.following.filter(followee__is_active=True).order_by(
                    '-created_at').all()[start_index:start_index + size]
                returned_user = [item.followee.id for item in friendships]
            else:
                if is_new:
                    from datetime import datetime, timedelta
                    threshold_time = datetime.now() - timedelta(days=3)
                    friendships = cur_user.followers.filter(
                        created_at__gt=threshold_time,
                        follower__is_active=True).order_by('-created_at').all()[
                        start_index:start_index + size]
                else:
                    friendships = cur_user.followers.filter(follower__is_active=True).all()[
                        start_index:start_index + size]

                returned_user = [item.follower.id for item in friendships]

        if is_rank:
            maininfo_serializer = MainInfoSerializer(
                Member.objects.filter(id__in=returned_user), many=True)
        else:
            maininfo_serializer = MainInfoSerializer(Member.objects.filter(
                id__in=returned_user).order_by('-created_at'), many=True)
        return Response(maininfo_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_total_friends(request):
    cur_user = request.user
    is_new = request.GET.get('is_new')
    is_active = request.GET.get('is_active')
    is_rank = request.GET.get('is_rank')
    if is_new and is_active and is_rank:
        if is_rank == "1":
            friendship_count = Member.objects.filter(
                is_active=True, is_superuser=False).count()
        else:
            if is_active == "1":
                friendship_count = cur_user.following.filter(
                    followee__is_active=True).count()
            else:
                if is_new == "1":
                    from datetime import datetime, timedelta
                    threshold_time = datetime.now() - timedelta(days=3)
                    friendship_count = cur_user.followers.filter(
                        created_at__gt=threshold_time, follower__is_active=True).count()
                else:
                    friendship_count = cur_user.followers.filter(
                        follower__is_active=True).count()
        return Response(friendship_count, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    from firebase_admin import auth as fire_auth

    curUser = request.user
    requestData = request.data
    if "user" in requestData.keys():
        # get user
        dataUser = requestData["user"]
        # print(dataUser)

        # if password exists
        if requestData["new_password"] != "":
            if curUser.social_type > 0:
                return Response({
                    "msg": "Password is not necessary with an email account"
                }, status=status.HTTP_400_BAD_REQUEST)

            newPassword = requestData["new_password"]

            # update password
            fire_auth.update_user(curUser.firebase_id, password=newPassword)

        # if email changed
        emailChanged = False
        if dataUser["email"] is not None and dataUser["email"].strip() != "":
            newEmail = dataUser["email"].strip()
            if newEmail != curUser.email:
                try:
                    # temperary
                    user_result = fire_auth.update_user(
                        curUser.firebase_id, email=newEmail, email_verified=False)
                    emailChanged = True
                except BaseException:
                    return Response({
                        "msg": "User email change failed"
                    }, status=status.HTTP_400_BAD_REQUEST)

        # delete avatar field if it does not exist
        if not requestData["avatar_set"]:
            dataUser.pop("avatar", None)

        newUserSerialzier = MemberSerializer(
            curUser, data=requestData["user"], partial=True)
        if newUserSerialzier.is_valid():
            newUserSerialzier.save()
            return Response({"data": newUserSerialzier.data,
                             "email_changed": emailChanged},
                            status=status.HTTP_200_OK)
        else:
            return Response({
                "msg": "User info invalid",
                "err": newUserSerialzier.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "msg": "User info does not exist"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followers(request):
    curUser = request.user
    friendships = curUser.following.filter(followee__is_active=True).all()
    followees = [item.followee.id for item in friendships]

    maininfo_serializer = MainInfoSerializer(
        Member.objects.filter(id__in=followees), many=True)
    return Response(maininfo_serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follow_user(request, id=None):
    follower_id = id
    user = request.user
    target_user = Member.objects.get(pk=follower_id)

    if user.id == follower_id:
        return Response(
            "You can not follow yourself",
            status.HTTP_400_BAD_REQUEST)
    else:
        cur_count = Friendship.objects.filter(
            follower=user, followee=target_user).count()
        if cur_count > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            Friendship.objects.create(follower=user, followee=target_user)
            return Response({"success": True}, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, id=None):
    unfollower_id = id
    user = request.user
    target_user = Member.objects.get(pk=unfollower_id)

    if user.id == unfollower_id:
        return Response(
            "You can not unfollow yourself",
            status.HTTP_400_BAD_REQUEST)
    else:
        cur_count = Friendship.objects.filter(
            follower=user, followee=target_user).count()
        if cur_count > 0:
            Friendship.objects.filter(
                follower=user, followee=target_user).delete()
            return Response({"success": True}, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
