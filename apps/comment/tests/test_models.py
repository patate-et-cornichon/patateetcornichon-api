import pytest
from django.core.exceptions import ValidationError

from apps.account.models import User
from apps.comment.models import Comment
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

    @pytest.mark.xfail(raises=ValidationError)
    def test_cannot_create_a_comment_without_author(self):
        recipe = RecipeFactory.create()

        comment_data = {
            'content': 'Blabla',
            'commented_object': recipe
        }
        comment = Comment(**comment_data)
        comment.full_clean()
