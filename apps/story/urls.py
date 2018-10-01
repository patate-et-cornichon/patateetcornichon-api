""" Story paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.story.views import StoryViewSet, UploadImageViewSet


router = DefaultRouter()
router.register(r'upload-image', UploadImageViewSet, base_name='upload_image')
router.register(r'', StoryViewSet, base_name='story')

app_name = 'story'
urlpatterns = [
    path('/', include(router.urls)),
]
