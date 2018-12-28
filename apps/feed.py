from itertools import chain

from django.contrib.syndication.views import Feed

from apps.recipe.models import Recipe
from apps.story.models import Story


class LatestPostsFeed(Feed):
    title = 'Patate & Cornichon'
    description = 'Cuisine végane et articles intelligents'
    link = '/'
    limit = 10

    def items(self):
        """ Returns two sorts of items: the recipes and the stories. """
        recipes = Recipe.objects.filter(published=True).order_by('-created')[:self.limit]
        stories = Story.objects.filter(published=True).order_by('-created')[:self.limit]
        return sorted(
            chain(recipes, stories),
            key=lambda post: post.created,
            reverse=True,
        )[:self.limit]

    def item_title(self, item):
        """ Returns the full title of the post. """
        return item.full_title

    def item_description(self, item):
        """ Returns the meta description of the post. """
        return item.meta_description

    def item_link(self, item):
        """ Sets Post URL. """
        if isinstance(item, Recipe):
            prefix = 'recettes'
        else:
            prefix = 'blog'
        return f'/{prefix}/' + item.slug
