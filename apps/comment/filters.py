from django_filters import rest_framework as filters

from apps.comment.constants import VALID_CONTENT_TYPES

from .models import Comment


class CommentFilter(filters.FilterSet):
    """ Filter through ``Comment`` instances. """

    content_type = filters.ChoiceFilter(choices=VALID_CONTENT_TYPES, lookup_expr='model')
    object_id = filters.UUIDFilter(method='filter_object_id')

    class Meta:
        model = Comment
        fields = [
            'content_type',
            'object_id',
        ]

    def filter_object_id(self, queryset, name, value):
        """ If we want comments associated with an object id, we just want to return
            comments without parent.
        """
        qs = queryset.filter(object_id=value, parent__isnull=True)
        return qs
