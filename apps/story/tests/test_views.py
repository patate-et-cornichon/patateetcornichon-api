import json
import os
from base64 import b64encode

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import User

from ..models import Story, Tag
from .factories import StoryFactory, TagFactory


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestStoryViewSet:
    def test_can_access_published_stories_only_when_non_staff_user(self):
        StoryFactory.create(published=True)
        StoryFactory.create(published=True)
        StoryFactory.create(published=False)

        client = APIClient()
        response = client.get(reverse('story:story-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_can_access_all_stories_when_staff_user(self):
        StoryFactory.create(published=True)
        StoryFactory.create(published=True)
        StoryFactory.create(published=False)

        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_superuser(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('story:story-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_can_create_a_new_story_when_staff_user(self):
        tag_1 = TagFactory.create()

        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        author = User.objects.create_superuser(**user_data)

        with open(os.path.join(FIXTURE_ROOT, 'story.jpg'), 'rb') as main_picture:
            story_data = {
                'slug': 'devenir-zero-dechet',
                'published': True,
                'title': 'Devenir',
                'sub_title': 'zéro déchet',
                'full_title': 'Devenir zéro déchet',
                'main_picture': b64encode(main_picture.read()).decode('utf-8'),
                'tags': [
                    tag_1.name,
                    'zero déchet',
                ],
                'content': '<p>C\'est gentil pour la planète.</p>',
                'authors': [
                    str(author.id),
                ],
                'meta_description': 'Zéro déchet',
            }

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.post(
            reverse('story:story-list'),
            data=json.dumps(story_data),
            content_type='application/json',
        )
        assert response.status_code == status.HTTP_201_CREATED

        story = Story.objects.filter(slug=story_data['slug']).first()

        assert story is not None

        # Check if the pictures name are equal
        story_data.pop('main_picture')
        assert story.slug in story.main_picture.name

        # Check if the tags are valid
        story_data.pop('tags')
        assert tag_1 in story.tags.all()
        tag_2 = Tag.objects.get(name='zero déchet')
        assert tag_2 in story.tags.all()

        # Check if authors are valid
        story_data.pop('authors')
        assert author in story.authors.all()

        # Check data are well populated
        for key, value in story_data.items():
            assert getattr(story, key) == value

    def test_cannot_create_a_new_story_when_non_staff(self):
        story_data = {
            'slug': 'devenir-zero-dechet',
        }

        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_user(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.post(
            reverse('recipe:recipe-list'),
            story_data,
            content_type='application/json',
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        story = Story.objects.filter(slug=story_data['slug']).first()
        assert story is None


@pytest.mark.django_db
class TestUploadImageViewSet:
    def test_can_upload_an_image_when_staff(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_superuser(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])

        with open(os.path.join(FIXTURE_ROOT, 'story.jpg'), 'rb') as f:
            data = {
                'file': f,
            }
            response = client.post(
                reverse('story:upload_image-list'),
                data=data,
                format='multipart',
            )
        assert response.status_code == status.HTTP_200_OK

    def test_cannot_upload_non_image_file(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_superuser(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])

        file = SimpleUploadedFile('file.mp4', b'File content', content_type='video/mp4')
        data = {
            'file': file,
        }
        response = client.post(
            reverse('story:upload_image-list'),
            data=data,
            format='multipart',
        )
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    def test_can_not_upload_an_image_when_non_staff(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_user(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])

        with open(os.path.join(FIXTURE_ROOT, 'story.jpg'), 'rb') as f:
            data = {
                'file': f
            }
            response = client.post(
                reverse('story:upload_image-list'),
                data=data,
                format='multipart',
            )
        assert response.status_code == status.HTTP_403_FORBIDDEN
