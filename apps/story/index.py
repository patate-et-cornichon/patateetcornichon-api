from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Story


@register(Story)
class StoryIndex(AlgoliaIndex):
    """ Index representing published story. """

    index_name = 'story'
    should_index = 'published'
    fields = (
        'slug',
        'title',
        'sub_title',
        'full_title',
        'main_picture_thumbs',
        'created',
        'comments_count',
        'tags_list',
        'content',
    )
    settings = {
        'searchableAttributes': [
            'full_title',
            'tags_list',
            'content',
        ],
        'attributesForFaceting': [
            'tags_list.slug',
        ],
        'replicas': [
            'story_created_asc',
            'story_created_desc',
        ],
    }
