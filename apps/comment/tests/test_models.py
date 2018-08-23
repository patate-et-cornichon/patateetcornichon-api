import pytest
from django.core.exceptions import ValidationError

from apps.account.models import User
from apps.comment.models import Comment
from apps.comment.tests.factories import CommentFactory
from apps.recipe.tests.factories import RecipeFactory


@pytest.mark.django_db
class TestComment:
    def test_can_create_a_comment_with_registered_author(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Test',
        }
        user = User.objects.create(**user_data)

        recipe = RecipeFactory.create()

        comment_data = {
            'registered_author': user,
            'content': 'Blabla',
            'commented_object': recipe
        }
        comment = Comment.objects.create(**comment_data)

        assert comment.author == user
        assert comment.content == 'Blabla'
        assert comment.commented_object == recipe
        assert comment.content_type.app_label == 'recipe'
        assert comment.object_id == recipe.id

    def test_can_create_a_comment_with_unregistered_author(self):
        recipe = RecipeFactory.create()

        comment_data = {
            'unregistered_author': {
                'email': 'test@test.com',
                'first_name': 'Test'
            },
            'content': 'Blabla',
            'commented_object': recipe
        }
        comment = Comment.objects.create(**comment_data)

        assert comment.author.email == comment_data['unregistered_author']['email']
        assert comment.author.first_name == comment_data['unregistered_author']['first_name']

    def test_can_get_subscribers(self):
        user_data_1 = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Test',
        }
        user_1 = User.objects.create(**user_data_1)
        comment_1 = CommentFactory.create(be_notified=True, registered_author=user_1)
        comment_2 = CommentFactory.create(
            be_notified=False,
            parent=comment_1,
            unregistered_author={
                'email': 'test2@test.com',
                'first_name': 'Test'
            },
        )
        comment_3 = CommentFactory.create(
            be_notified=True,
            parent=comment_1,
            unregistered_author={
                'email': 'test3@test.com',
                'first_name': 'Test'
            },
        )
        user_data_2 = {
            'email': 'test4@test.com',
            'password': 'test',
            'first_name': 'Test',
        }
        user_2 = User.objects.create(**user_data_2)
        comment_4 = CommentFactory.create(
            be_notified=True, parent=comment_1, registered_author=user_2,
        )
        comment_5 = CommentFactory.create(
            be_notified=True, parent=comment_1, registered_author=user_1,
        )

        subscribers = comment_5.get_subscribers()

        assert len(subscribers) == 2

        assert comment_1.author.email not in subscribers
        assert comment_2.author.email not in subscribers
        assert comment_3.author.email in subscribers
        assert comment_4.author.email in subscribers
        assert comment_5.author.email not in subscribers

        comment_6 = CommentFactory.create(
            be_notified=True,
            parent=comment_1,
            unregistered_author={
                'email': 'test5@test.com',
                'first_name': 'Test'
            },
        )

        subscribers = comment_6.get_subscribers()

        assert len(subscribers) == 3
        assert comment_1.author.email in subscribers
        assert comment_6.author.email not in subscribers

    @pytest.mark.xfail(raises=ValidationError)
    def test_cannot_create_a_comment_without_author(self):
        recipe = RecipeFactory.create()

        comment_data = {
            'content': 'Blabla',
            'commented_object': recipe
        }
        comment = Comment(**comment_data)
        comment.full_clean()
