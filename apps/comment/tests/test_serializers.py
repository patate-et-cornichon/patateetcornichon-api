import os
import unittest.mock
import uuid

import pytest
from django.conf import settings as settings
from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.account.models import User
from apps.comment.models import Comment
from apps.comment.serializers import (
    CommentCreateUpdateSerializer, CommentRetrieveSerializer, UnregisteredAuthorSerializer)
from apps.comment.tests.factories import CommentFactory
from apps.recipe.tests.factories import RecipeFactory
from apps.story.tests.factories import StoryFactory
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

    def test_can_send_an_email_notification_to_subscribers(self):
        parent_comment = CommentFactory.create(be_notified=True)
        comment_data = {
            'content': 'Blabla',
            'content_type': 'recipe',
            'object_id': self.recipe.id,
            'parent': parent_comment.id
        }
        serializer = CommentCreateUpdateSerializer(
            data=comment_data,
            context={'request': self.request},
        )
        assert serializer.is_valid()

        instance = serializer.save()

        assert len(mail.outbox) == 0

        instance.is_valid = True
        instance.save()
        serializer = CommentCreateUpdateSerializer(
            data={'is_valid': True},
            instance=instance,
            partial=True,
            context={'request': self.request},
        )

        assert serializer.is_valid()

        serializer.save()

        assert len(mail.outbox) == 1
        assert parent_comment.author.email in mail.outbox[0].bcc

    def test_can_return_a_default_author_avatar(self):
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

        assert 'default_avatar' in serializer._get_author_avatar()

    def test_can_return_the_unregistered_author_avatar(self):
        comment = CommentFactory.create(unregistered_author={
            'email': 'Test@test.com',
            'first_name': 'Test',
            'avatar': '/toto/toto.jpg',
        })

        serializer = CommentCreateUpdateSerializer(
            instance=comment,
            context={'request': self.request},
        )

        assert '/toto/toto.jpg' in serializer._get_author_avatar()

    def test_can_return_the_registered_author_avatar(self):
        with open(os.path.join(FIXTURE_ROOT, 'cartman.jpg'), 'rb') as f:
            self.user.avatar.save('cartman.jpg', ContentFile(f.read()))

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

        assert 'cartman.jpg' in serializer._get_author_avatar()

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

    def test_can_return_a_default_avatar_absolute_uri(self):
        factory = APIRequestFactory()
        request = factory.get('/')

        unregistered_author_data = {
            'email': 'test@test.com',
            'first_name': 'Test',
        }
        serializer = UnregisteredAuthorSerializer(
            data=unregistered_author_data,
            context={'request': request},
        )
        avatar_index = len(unregistered_author_data['email']) % 8 + 1
        avatar_name = f'comment/avatars/default_avatar_{avatar_index}.svg'

        assert avatar_name in serializer.get_avatar(unregistered_author_data)


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

    def test_can_return_commented_object_data(self):
        factory = APIRequestFactory()
        request = factory.get('/')

        recipe_post = RecipeFactory.create()
        story_post = StoryFactory.create()

        comment_1 = CommentFactory.create(commented_object=recipe_post)
        comment_2 = CommentFactory.create(commented_object=story_post)

        serializer = CommentRetrieveSerializer(
            context={'request': request},
        )
        assert serializer.get_commented_object(comment_1) == {
            'full_title': recipe_post.full_title,
            'slug': recipe_post.slug,
        }
        assert serializer.get_commented_object(comment_2) == {
            'full_title': story_post.full_title,
            'slug': story_post.slug,
        }
