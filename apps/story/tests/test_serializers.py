import os
from base64 import b64encode

import pytest

from apps.account.models import User
from apps.story.models import Tag

from ..models import Story
from ..serializers import StoryCreateUpdateSerializer
from .factories import TagFactory


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestStoryCreateUpdateSerializer:
    @pytest.fixture(autouse=True)
    def setup(self):
        author_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        self.author = User.objects.create_user(**author_data)

    def test_can_create_a_story_instance(self):
        tag_1 = TagFactory.create()

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
                  self.author.id,
                ],
                'meta_description': 'Zéro déchet',
            }

        serializer = StoryCreateUpdateSerializer(data=story_data)
        assert serializer.is_valid()

        serializer.save()

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
        assert self.author in story.authors.all()

        # Check data are well populated
        for key, value in story_data.items():
            assert getattr(story, key) == value
