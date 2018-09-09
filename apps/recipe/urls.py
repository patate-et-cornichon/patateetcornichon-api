""" Recipe paths """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, IngredientViewSet, RecipeViewSet, TagViewSet, UnitViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, base_name='category')
router.register(r'tags', TagViewSet, base_name='tag')
router.register(r'ingredients', IngredientViewSet, base_name='ingredient')
router.register(r'units', UnitViewSet, base_name='unit')
router.register(r'', RecipeViewSet, base_name='recipe')

app_name = 'recipe'
urlpatterns = [
    path('/', include(router.urls)),
]
