import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recipe.models import Recipe
from apps.recipe.serializers import RecipeSerializer

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestRecipeSerializer:
    def test_can_create_a_recipe_instance(self):
        recipe_data = {
            'slug': 'super-recette',
            'title': 'Crêpes',
            'sub_title': 'vegan',
            'full_title': 'Crêpes vegan au chocolat',
            'main_picture': SimpleUploadedFile(
                name='recipe.jpg',
                content=open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb').read(),
                content_type='image/jpeg'
            ),
            'goal': '2 pers.',
            'preparation_time': 30,
            'introduction': 'Hello world',
            'meta_description': 'Recettes de crêpes vegan',
            'steps': [
                'Ajouter la farine',
                'Ajouter le lait végétal',
            ],
        }

        serializer = RecipeSerializer(data=recipe_data)
        assert serializer.is_valid()

        serializer.save()

        recipe = Recipe.objects.filter(slug=recipe_data['slug']).first()
        assert recipe is not None

        # Check if the pictures name are equal
        recipe_data.pop('main_picture')
        assert recipe.slug in recipe.main_picture.name

        # Check data are well populated
        for key, value in recipe_data.items():
            assert getattr(recipe, key) == value

    def test_cannot_create_a_recipe_instance_if_no_step(self):
        recipe_data = {
            'slug': 'super-recette',
            'title': 'Crêpes',
            'sub_title': 'vegan',
            'full_title': 'Crêpes vegan au chocolat',
            'main_picture': SimpleUploadedFile(
                name='recipe.jpg',
                content=open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb').read(),
                content_type='image/jpeg'
            ),
            'goal': '2 pers.',
            'preparation_time': 30,
            'introduction': 'Hello world',
            'meta_description': 'Recettes de crêpes vegan',
        }

        serializer = RecipeSerializer(data=recipe_data)
        assert not serializer.is_valid()
        assert 'steps' in serializer.errors