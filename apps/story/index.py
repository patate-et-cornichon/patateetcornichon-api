from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Story


@register(Story)
class StoryIndex(AlgoliaIndex):
    """ Index representing published story. """

    should_index = 'published'
    fields = (
        'slug',
        'full_title',
        'main_picture_thumbs',
        'created',
        'tags_list',
        'content',
    )
    settings = {
        'searchableAttributes': [
            'full_title',
            'tags_list',
            'content',
        ],
        'unretrievableAttributes': [
            'content',
        ]
    }
