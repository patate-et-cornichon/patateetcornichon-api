import pytest

from apps.comment.filters import CommentFilter
from apps.comment.models import Comment
from apps.comment.tests.factories import CommentFactory


@pytest.mark.django_db
class TestCommentFilter:
    def test_can_filter_children_comments_with_object_id(self):
        comment_1 = CommentFactory.create()
        comment_2 = CommentFactory.create(parent=comment_1)
        comment_3 = CommentFactory.create(parent=comment_1)

        qs = Comment.objects.all()
        filter = CommentFilter(
            data={'object_id': comment_1.commented_object.id},
            queryset=qs,
        )
        result = filter.qs

        assert comment_1 in result
        assert comment_2 not in result
        assert comment_3 not in result
