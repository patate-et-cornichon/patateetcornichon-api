""" Recipe paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, RecipeViewSet


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, base_name='recipe')
router.register(r'categories', CategoryViewSet, base_name='category')

app_name = 'recipe'
urlpatterns = [
    path('/', include(router.urls)),
]
