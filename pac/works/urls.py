from django.urls import path, include
from .views import *
from django.conf.urls import url

urlpatterns = [
    path('', WorksView.as_view(), name = "get_works"),
    path('<int:pk>', WorksDetail.as_view(), name = "work_detail"),
    path('like/<int:id>', like_work, name = "work_like"),
    path('comment', CommentView.as_view(), name = "work_comment"),
    path('media', UploadGallery.as_view(), name = "upload_gallery"),
    path('ccsettings', CcSettingView.as_view(), name = "cc_settings"),
    path('comments', get_work_comment, name = "comments"),
    path('tags', get_related_tags, name = "related_tags"),
]