import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import model_to_dict

from apps.recipe.models import Recipe
from apps.recipe.tests.factories import (
    RecipeCompositionFactory, RecipeFactory, RecipeSelectionFactory, TagFactory)

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

    def test_can_return_tags_list(self):
        tags = TagFactory.create_batch(2)

        recipe = RecipeFactory.create()
        recipe.tags.add(*tags)

        assert recipe.tags_list == [
            model_to_dict(tag, fields=['slug', 'name'])
            for tag in tags
        ]

    def test_can_return_categories_list(self):
        categories = CategoryFactory.create_batch(2)

        recipe = RecipeFactory.create()
        recipe.categories.add(*categories)

        assert recipe.categories_list == [
            model_to_dict(category, fields=['slug', 'name'])
            for category in categories
        ]

    def test_can_return_thumbnails(self):
        recipe = RecipeFactory.create()
        with open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb') as f:
            recipe.secondary_picture = SimpleUploadedFile(
                name='recipe.jpg',
                content=f.read(),
                content_type='image/jpeg'
            )
            recipe.save()

        assert 'large' in recipe.secondary_picture_thumbs.keys()

    def test_can_return_total_time(self):
        recipe = RecipeFactory.create(
            preparation_time=20,
            cooking_time=30,
        )
        assert recipe.total_time == 50


@pytest.mark.django_db
class TestRecipeSelection:
    def test_can_return_thumbnails(self):
        selection = RecipeSelectionFactory.create()
        with open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb') as f:
            selection.picture = SimpleUploadedFile(
                name='recipe.jpg',
                content=f.read(),
                content_type='image/jpeg'
            )
            selection.save()

        assert 'large' in selection.picture_thumbs.keys()
        assert 'extra_large' in selection.picture_thumbs.keys()
