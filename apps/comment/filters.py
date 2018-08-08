from django_filters import rest_framework as filters

from apps.comment.constants import VALID_CONTENT_TYPES

from .models import Comment


class CommentFilter(filters.FilterSet):
    content_type = filters.ChoiceFilter(choices=VALID_CONTENT_TYPES, lookup_expr='app_label')

    class Meta:
        model = Comment
        fields = [
            'content_type',
            'object_id',
        ]
