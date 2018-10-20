from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Story


@register(Story)
class StoryIndex(AlgoliaIndex):
    """ Index representing published story. """

    should_index = 'published'
    fields = (
        'slug',
        'title',
        'sub_title',
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
        ],
        'attributesForFaceting': [
            'tags_list.slug',
        ],
    }
