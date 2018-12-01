from django_filters import rest_framework as filters

from apps.recipe.models import Recipe
from common.drf.filters import MultiCharFilter


class RecipeFilter(filters.FilterSet):

    slug__exclude = MultiCharFilter(field_name='slug', exclude=True)
    exclude__last = filters.NumberFilter(method='filter_exclude__last')

    def filter_exclude__last(self, qs, name, value):  # pragma: no cover
        """ Exclude last recipes from queryset. """
        last_recipes_ids = qs.order_by('-created')[:value].values_list('id', flat=True)
        return qs.exclude(pk__in=last_recipes_ids)

    class Meta:
        model = Recipe
        fields = {
            'full_title': ['startswith', 'istartswith', 'contains', 'icontains'],
            'slug': ['exact'],
            'categories__slug': ['exact'],
            'created': ['lte', 'gte', 'lt', 'gt'],
        }
