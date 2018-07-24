import os
from base64 import b64encode

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recipe.models import Recipe
from apps.recipe.serializers import RecipeCreateUpdateSerializer
from apps.recipe.tests.factories import CategoryFactory, TagFactory


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestRecipeCreateUpdateSerializer:
    def test_can_create_a_recipe_instance(self):
        category_1 = CategoryFactory.create()
        category_2 = CategoryFactory.create(parent=category_1)

        with open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb') as main_picture:
            recipe_data = {
                'slug': 'super-recette',
                'title': 'Crêpes',
                'sub_title': 'vegan',
                'full_title': 'Crêpes vegan au chocolat',
                'main_picture': b64encode(main_picture.read()).decode('utf-8'),
                'categories': [
                    category_1.id,
                    category_2.id,
                ],
                'goal': '2 pers.',
                'preparation_time': 30,
                'introduction': 'Hello world',
                'ingredients': [
                    {
                        'ingredient': 'Eau',
                    },
                    {
                        'ingredient': 'Olives',
                        'quantity': 2,
                    },
                    {
                        'ingredient': 'Patates',
                        'unit': 'gr',
                        'quantity': 2,
                    },
                    {
                        'ingredient': 'Sucre',
                        'unit': 'gr',
                        'quantity': 3,
                    },
                ],
                'steps': [
                    'Ajouter la farine',
                    'Ajouter le lait végétal',
                ],
                'meta_description': 'Recettes de crêpes vegan',
            }

        serializer = RecipeCreateUpdateSerializer(data=recipe_data)
        assert serializer.is_valid()

        serializer.save()

        recipe = Recipe.objects.filter(slug=recipe_data['slug']).first()
        assert recipe is not None

        # Check if the pictures name are equal
        recipe_data.pop('main_picture')
        assert recipe.slug in recipe.main_picture.name

        # Check if the categories are valid
        recipe_data.pop('categories')
        assert category_1 in recipe.categories.all()
        assert category_2 in recipe.categories.all()

        # Check if the categories are valid
        ingredients = recipe_data.pop('ingredients')
        for ingredients_item in ingredients:
            ingredient_name = ingredients_item['ingredient']
            recipe_ingredient = (
                recipe.ingredients
                .filter(ingredient__name=ingredient_name)
                .first()
            )
            assert recipe_ingredient is not None
            assert recipe_ingredient.quantity == ingredients_item.get('quantity')
            if recipe_ingredient.unit:
                assert recipe_ingredient.unit.name == ingredients_item['unit']

        # Check data are well populated
        for key, value in recipe_data.items():
            assert getattr(recipe, key) == value

    def test_can_create_tags_with_new_recipe_instance(self):
        category_1 = CategoryFactory.create()
        category_2 = CategoryFactory.create(parent=category_1)
        tag = TagFactory.create()

        with open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb') as main_picture:
            recipe_data = {
                'slug': 'super-recette',
                'title': 'Crêpes',
                'sub_title': 'vegan',
                'full_title': 'Crêpes vegan au chocolat',
                'main_picture': b64encode(main_picture.read()).decode('utf-8'),
                'categories': [
                    category_1.id,
                    category_2.id,
                ],
                'tags': [
                    tag.name,
                    'Food',
                    'Miam',
                ],
                'goal': '2 pers.',
                'preparation_time': 30,
                'introduction': 'Hello world',
                'ingredients': [
                    {
                        'ingredient': 'Patates',
                        'unit': 'gr',
                        'quantity': 2,
                    },
                    {
                        'ingredient': 'Sucre',
                        'unit': 'gr',
                        'quantity': 3,
                    },
                ],
                'steps': [
                    'Ajouter la farine',
                    'Ajouter le lait végétal',
                ],
                'meta_description': 'Recettes de crêpes vegan',
            }
        serializer = RecipeCreateUpdateSerializer(data=recipe_data)
        assert serializer.is_valid()

        serializer.save()

        recipe = Recipe.objects.filter(slug=recipe_data['slug']).first()
        assert recipe is not None

        assert recipe.tags.filter(id=tag.id).first() is not None
        assert recipe_data['tags'][1] in list(recipe.tags.values_list('name', flat=True))
        assert recipe_data['tags'][2] in list(recipe.tags.values_list('name', flat=True))

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

        serializer = RecipeCreateUpdateSerializer(data=recipe_data)
        assert not serializer.is_valid()
        assert 'steps' in serializer.errors
