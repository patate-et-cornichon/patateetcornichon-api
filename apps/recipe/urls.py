""" Recipe paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, IngredientViewSet, RecipeViewSet, TagViewSet, UnitViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'', RecipeViewSet, basename='recipe')

app_name = 'recipe'
urlpatterns = [
    path('', include(router.urls)),
]
