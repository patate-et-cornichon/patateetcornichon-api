import pytest

from apps.recipe.files import (
    recipe_main_picture_directory_path, recipe_secondary_picture_directory_path)
from apps.recipe.tests.factories import RecipeFactory


@pytest.mark.django_db
class TestRecipeMainPictureDirectoryPath:
    def test_can_returns_path_with_recipe_slug(self):
        recipe = RecipeFactory.create()
        path = recipe_main_picture_directory_path(recipe, 'filename.jpg')
        assert path == f'recipes/{recipe.slug}.jpg'


@pytest.mark.django_db
class TestRecipeSecondaryPictureDirectoryPath:
    def test_can_returns_path_with_recipe_slug(self):
        recipe = RecipeFactory.create()
        path = recipe_secondary_picture_directory_path(recipe, 'filename.jpg')
        assert path == f'recipes/{recipe.slug}-2.jpg'
