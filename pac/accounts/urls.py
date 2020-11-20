from django.urls import path, include
from .views import *
from django.conf.urls import url

# not using firebase
# urlpatterns = [
#     path('facebook/login', facebook_login, name="facebook_login"),
#     path('google/login', google_login, name="google_login"),
#     path('email/register', MemberCreate.as_view(), name="email_register"),
#     path('email/login', LoginUserView.as_view(), name="email_login"),
#     path('password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
#     path('<str:email>/<str:email_token>', verify_email, name="verify_token"),
# ]

# using firebase
urlpatterns = [
    path('', edit_profile, name = "edit_profile"),
    path('members', UserView.as_view(), name = "members"),
    path('authorize', LoginUserView.as_view(), name = "authorize"),
    path('info', get_user_profile, name = "info"),
    path('info/<int:pk>', UserDetail.as_view(), name = "user_detail"),
    path('maininfo/<int:pk>', MainInfo.as_view(), name = "user_maininfo"),
    path('init', InitRegisterView.as_view(), name = "initregister"),
    path('follows', get_friendship_user, name = "follow"),
    path('follows/<int:id>', follow_user, name = "follow_user"),
    path('unfollows/<int:id>', unfollow_user, name = "unfollow_user"),
    path('follow_total', get_total_friends, name = "follow_total"),
    path('followers', get_followers, name = "followers"),
    path('banner', BannerView.as_view(), name = "banner"),
    path('genre', GenreView.as_view(), name = "genre")
]
