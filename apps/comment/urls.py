""" Comment paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet


router = DefaultRouter()
router.register(r'', CommentViewSet, base_name='comment')

app_name = 'comment'
urlpatterns = [
    path('', include(router.urls)),
]
