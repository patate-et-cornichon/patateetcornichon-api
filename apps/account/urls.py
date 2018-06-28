""" Account paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet


router = DefaultRouter()
router.register(r'', UserViewSet, base_name='user')

app_name = 'account'
urlpatterns = [
    path('/', include(router.urls)),
]
