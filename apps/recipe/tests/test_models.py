import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recipe.models import Recipe
from apps.recipe.tests.factories import RecipeCompositionFactory

from .factories import CategoryFactory


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestRecipe:
    def test_can_create_a_recipe(self):
        categories = CategoryFactory.create_batch(2)
        composition = RecipeCompositionFactory.create_batch(7)

        recipe_data = {
            'title': 'Chocolatine',
            'sub_title': 'vegan',
            'full_title': 'Chocolatine vegan',
            'main_picture': SimpleUploadedFile(
                name='recipe.jpg',
                content=open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb').read(),
                content_type='image/jpeg'
            ),
            'goal': '1 pers.',
            'preparation_time': 23,
            'difficulty': Recipe.MEDIUM,
            'steps': [
                'Epluche les bananes',
                'Mange les bananes',
            ],
            'meta_description': 'Banana Recipe'
        }
        recipe = Recipe.objects.create(**recipe_data)
        recipe.categories.add(*categories)
        recipe.composition.add(*composition)

        # Check if the pictures name are equal
        recipe_data.pop('main_picture')
        assert recipe.slug in recipe.main_picture.name

        # Check data are well populated
        for key, value in recipe_data.items():
            assert getattr(recipe, key) == value

        # Check relative models
        assert list(recipe.categories.all()) == categories
        assert list(recipe.composition.all()) == composition
