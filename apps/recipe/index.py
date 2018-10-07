from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Recipe


@register(Recipe)
class RecipeIndex(AlgoliaIndex):
    """ Index representing published recipe. """

    should_index = 'published'
    fields = (
        'slug',
        'full_title',
        'main_picture',
        'created',
        'tags_list',
        'categories_list',
    )
    settings = {
        'searchableAttributes': [
            'full_title',
            'tags_list',
            'categories_list',
        ],
    }
    index_name = 'recipe'
