""" Recipe paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, RecipeViewSet, TagViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, base_name='category')
router.register(r'tags', TagViewSet, base_name='tag')
router.register(r'', RecipeViewSet, base_name='recipe')

app_name = 'recipe'
urlpatterns = [
    path('/', include(router.urls)),
]
