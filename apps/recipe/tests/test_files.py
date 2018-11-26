import pytest

from apps.recipe.files import (
    recipe_main_picture_directory_path, recipe_secondary_picture_directory_path,
    selection_picture_directory_path)
from apps.recipe.tests.factories import RecipeFactory, RecipeSelectionFactory


@pytest.mark.django_db
def test_can_returns_main_picture_path_with_recipe_slug():
    recipe = RecipeFactory.create()
    path = recipe_main_picture_directory_path(recipe, 'filename.jpg')
    assert path == f'recipes/{recipe.slug}.jpg'


@pytest.mark.django_db
def test_can_returns_secondary_picture_path_with_recipe_slug():
    recipe = RecipeFactory.create()
    path = recipe_secondary_picture_directory_path(recipe, 'filename.jpg')
    assert path == f'recipes/{recipe.slug}-2.jpg'


@pytest.mark.django_db
def test_can_returns_path_with_selection_slug():
    selection = RecipeSelectionFactory.create()
    path = selection_picture_directory_path(selection, 'filename.jpg')
    assert path == f'recipes/selections/{selection.slug}.jpg'
