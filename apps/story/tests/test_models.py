import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import model_to_dict
from django.utils.html import strip_tags
from django.utils.text import Truncator

from apps.account.models import User
from apps.story.tests.factories import StoryFactory

from ..models import Story
from .factories import TagFactory


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestStory:
    @pytest.fixture(autouse=True)
    def setup(self):
        author_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        self.author = User.objects.create_user(**author_data)

    def test_can_create_a_story(self):
        tags = TagFactory.create_batch(2)

        with open(os.path.join(FIXTURE_ROOT, 'story.jpg'), 'rb') as f:
            story_data = {
                'title': 'Devenir',
                'sub_title': 'zéro déchet',
                'full_title': 'Devenir zéro déchet',
                'main_picture': SimpleUploadedFile(
                    name='story.jpg',
                    content=f.read(),
                    content_type='image/jpeg'
                ),
                'content': '<p>C\'est gentil pour la planète.</p>',
                'meta_description': 'Zéro déchet',
            }
        story = Story.objects.create(**story_data)
        story.tags.add(*tags)
        story.authors.add(self.author)

        # Check if the pictures name are equal
        story_data.pop('main_picture')
        assert story.slug in story.main_picture.name

        # Check data are well populated
        for key, value in story_data.items():
            assert getattr(story, key) == value

        # Check relative models
        assert list(story.tags.all()) == tags
        assert story.authors.all()[0] == self.author

    def test_can_return_tags_list(self):
        tags = TagFactory.create_batch(2)

        story = StoryFactory.create()
        story.tags.add(*tags)

        assert story.tags_list == [
            model_to_dict(tag, fields=['slug', 'name'])
            for tag in tags
        ]

    def test_can_return_content_preview(self):
        story = StoryFactory.create()

        assert story.content_preview == Truncator(strip_tags(story.content_preview)).chars(300)
