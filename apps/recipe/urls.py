""" Account paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet


router = DefaultRouter()
router.register(r'', RecipeViewSet, base_name='recipe')

app_name = 'recipe'
urlpatterns = [
    path('/', include(router.urls)),
]
