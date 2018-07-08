from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Category, Recipe
from .serializers import CategorySerializer, RecipeCreateUpdateSerializer, RecipeRetrieveSerializer


class RecipeViewSet(ModelViewSet):
    """ Provide all methods for manage Recipe. """

    queryset = Recipe.objects.all()

    def get_permissions(self):
        """Instantiates and returns the list of permissions that this view requires. """
        if self.action in ['retrieve', 'list']:
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


class CategoryViewSet(ListModelMixin, GenericViewSet):
    """ Provide a list view for Category. """

    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
