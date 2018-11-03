""" Story paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.story.views import AuthorViewSet, StoryViewSet, TagViewSet, UploadImageViewSet


router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'upload-image', UploadImageViewSet, basename='upload_image')
router.register(r'', StoryViewSet, basename='story')

app_name = 'story'
urlpatterns = [
    path('', include(router.urls)),
]
