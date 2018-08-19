import json

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import User
from apps.comment.models import Comment
from apps.comment.tests.factories import CommentFactory
from apps.recipe.tests.factories import RecipeFactory


@pytest.mark.django_db
class TestCommentViewSet:
    def test_cannot_access_non_valid_comment_only_when_non_staff_user(self):
        CommentFactory.create(is_valid=False)
        CommentFactory.create(is_valid=False)
        CommentFactory.create(is_valid=True)

        client = APIClient()
        response = client.get(reverse('comment:comment-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_can_access_all_comments_only_when_staff_user(self):
        CommentFactory.create(is_valid=False)
        CommentFactory.create(is_valid=False)
        CommentFactory.create(is_valid=True)

        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_superuser(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('comment:comment-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_can_create_a_new_comment(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_user(**user_data)

        recipe = RecipeFactory.create()

        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': str(recipe.id),
        }

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.post(
            reverse('comment:comment-list'),
            data=json.dumps(comment_data),
            content_type='application/json',
        )
        assert response.status_code == status.HTTP_201_CREATED

        comment = Comment.objects.filter(registered_author__email=user_data['email']).first()
        assert comment.author == user
