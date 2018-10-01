""" Story paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.story.views import AuthorViewSet, StoryViewSet, TagViewSet, UploadImageViewSet


router = DefaultRouter()
router.register(r'authors', AuthorViewSet, base_name='author')
router.register(r'tags', TagViewSet, base_name='tag')
router.register(r'upload-image', UploadImageViewSet, base_name='upload_image')
router.register(r'', StoryViewSet, base_name='story')

app_name = 'story'
urlpatterns = [
    path('/', include(router.urls)),
]
