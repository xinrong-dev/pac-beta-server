from django.urls import path, include
from .views import *
from django.conf.urls import url

urlpatterns = [
    path('users', UserView.as_view(), name="users"),
    path('messages', MessageView.as_view(), name="messages"),
    path('reset/<int:id>', reset_message, name="reset"),
]
