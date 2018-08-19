import os
import unittest.mock
import uuid

import pytest
from django.conf import settings as settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.account.models import User
from apps.comment.models import Comment
from apps.comment.serializers import (
    CommentCreateUpdateSerializer, CommentRetrieveSerializer, UnregisteredAuthorSerializer)
from apps.recipe.tests.factories import RecipeFactory
from common.avatar import generate_avatar_name


FIXTURE_ROOT = os.path.join(settings.BASE_DIR, '../common/tests/fixtures')


@pytest.mark.django_db
class TestCommentCreateUpdateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        self.user = User.objects.create_user(**user_data)

        factory = APIRequestFactory()
        self.request = factory.get('/')
        self.request.user = self.user

        self.recipe = RecipeFactory.create()

    def test_can_create_a_new_comment(self):
        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': self.recipe.id,
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert serializer.is_valid()

        serializer.save()

        comment = Comment.objects.filter(registered_author=self.user).first()
        assert comment is not None
        assert comment.content == comment_data['content']
        assert comment.commented_object == self.recipe

    def test_cannot_be_valid_if_comment_owned_by_non_staff_user(self):
        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': self.recipe.id,
            'is_valid': True,
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert serializer.is_valid()

        serializer.save()

        comment = Comment.objects.filter(registered_author=self.user).first()
        assert comment is not None
        assert comment.is_valid is False

    def test_can_set_comment_to_be_valid_if_owned_by_staff_user(self):
        self.user.is_staff = True
        self.user.save()

        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': self.recipe.id,
            'is_valid': True,
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert serializer.is_valid()

        serializer.save()

    @pytest.mark.xfail(raises=ValidationError)
    def test_can_raise_an_error_when_object_does_not_exist(self):
        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': uuid.uuid4(),
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert serializer.is_valid()
        assert serializer.save()

    @unittest.mock.patch('requests.get')
    def test_can_fetch_an_avatar_for_unregistered_author(self, mocked_get):
        with open(os.path.join(FIXTURE_ROOT, 'cartman.jpg'), 'rb') as f:
            mocked_get.return_value = unittest.mock.Mock(
                status_code=200,
                content=f.read(),
            )

        self.request.user = AnonymousUser()

        comment_data = {
            'content': 'Blabla',
            'unregistered_author': {
                'email': 'test@test.com',
                'first_name': 'Test',
            },
            'content_type': 'recipe',
            'object_id': self.recipe.id,
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert serializer.is_valid()

        serializer.save()

        comment = (
            Comment.objects
            .filter(
                unregistered_author__email=comment_data['unregistered_author']['email']
            )
            .first()
        )
        assert comment.author.avatar is not None
        assert generate_avatar_name('test@test.com', '.jpg') in comment.author.avatar

    def test_cannot_validate_a_comment_without_author(self):
        self.request.user = AnonymousUser()

        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': uuid.uuid4(),
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestUnregisteredAuthorSerializer:
    def test_can_return_avatar_absolute_uri(self):
        factory = APIRequestFactory()
        request = factory.get('/')

        unregistered_author_data = {
            'email': 'test@test.com',
            'first_name': 'Test',
            'avatar': '/avatar/fetched/toto.jpg'
        }
        serializer = UnregisteredAuthorSerializer(
            data=unregistered_author_data,
            context={'request': request},
        )
        full_avatar_uri = serializer.get_avatar(unregistered_author_data)
        assert full_avatar_uri.endswith(unregistered_author_data['avatar'])


@pytest.mark.django_db
class TestCommentRetrieveSerializer:
    def test_can_set_children_field_if_object_id_is_provided(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        request.GET = request.GET.copy()
        request.GET['object_id'] = uuid.uuid4()

        serializer = CommentRetrieveSerializer(context={'request': request})
        assert 'children' in serializer.fields

    def test_can_remove_children_field_if_object_id_is_not_provided(self):
        factory = APIRequestFactory()
        request = factory.get('/')

        serializer = CommentRetrieveSerializer(context={'request': request})
        assert 'children' not in serializer.fields
