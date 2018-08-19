from rest_framework.viewsets import ModelViewSet

from .filters import CommentFilter
from .models import Comment
from .serializers import CommentCreateUpdateSerializer, CommentRetrieveSerializer


class CommentViewSet(ModelViewSet):
    """ Provide all methods for manage Comment. """

    queryset = Comment.objects.all()
    filterset_class = CommentFilter

    def get_queryset(self):
        """ Customize the queryset according to the current user. """
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(is_valid=True)

    def get_serializer_class(self):
        """ Return a dedicated serializer according to the HTTP verb. """
        if self.action not in ['retrieve', 'list']:
            return CommentCreateUpdateSerializer
        return CommentRetrieveSerializer
