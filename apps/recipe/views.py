from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.drf.mixins import CacheMixin
from common.drf.pagination import StandardResultsSetPagination

from .models import Category, Ingredient, Recipe, Tag, Unit
from .serializers import (
    CategorySerializer, IngredientSerializer, RecipeCreateUpdateSerializer,
    RecipeRetrieveSerializer, TagSerializer, UnitSerializer)


class RecipeViewSet(CacheMixin, ModelViewSet):
    """ Provide all methods for manage Recipe. """

    queryset = Recipe.objects.all()
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = {
        'categories__slug': ['exact'],
        'created': ['lte', 'gte', 'lt', 'gt'],
    }
    ordering_fields = ('created', 'views', '?',)
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """ Instantiates and returns the list of permissions that this view requires. """
        if self.action in ['retrieve', 'list', 'add_view']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """ Customize the queryset according to the current user. """
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(published=True)

    def get_serializer_class(self):
        """ Return a dedicated serializer according to the HTTP verb. """
        if self.action not in ['retrieve', 'list']:
            return RecipeCreateUpdateSerializer
        return RecipeRetrieveSerializer

    @action(detail=True, methods=['post'], url_name='add_view')
    def add_view(self, request, slug=None):
        """ Increments the recipe views. """
        recipe = self.get_object()
        recipe.views += 1
        recipe.save()
        return Response(status=status.HTTP_200_OK)


class CategoryViewSet(ListModelMixin, GenericViewSet):
    """ Provide a list view for Category. """

    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer


class TagViewSet(ListModelMixin, GenericViewSet):
    """ Provide a list view for Tag. """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListModelMixin, GenericViewSet):
    """ Provide a list view for Tag. """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UnitViewSet(ListModelMixin, GenericViewSet):
    """ Provide a list view for Tag. """

    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
