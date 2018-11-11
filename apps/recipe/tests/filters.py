import pytest
from django.utils import timezone

from apps.recipe.filters import RecipeFilter
from apps.recipe.models import Recipe
from apps.recipe.tests.factories import RecipeFactory


@pytest.mark.django_db
class TestRecipeFilter:
    def test_can_exclude_last_recipes(self):
        recipe_1 = RecipeFactory.create()  # noqa
        recipe_2 = RecipeFactory.create(
            created=timezone.now() - timezone.timedelta(hours=2),
        )

        qs = Recipe.objects.all()
        filter = RecipeFilter(
            data={'exclude__last': 1},
            queryset=qs,
        )
        result = filter.qs

        assert list(result) == [recipe_2]
