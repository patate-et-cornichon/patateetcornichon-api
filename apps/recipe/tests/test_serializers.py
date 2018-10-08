import os
from base64 import b64encode

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recipe.models import Recipe, RecipeIngredient
from apps.recipe.serializers import (
    RecipeCompositionSerializer, RecipeCreateUpdateSerializer, RecipeIngredientSerializer,
    RecipeRetrieveSerializer)
from apps.recipe.tests.factories import (
    CategoryFactory, RecipeFactory, RecipeIngredientFactory, TagFactory, UnitFactory)


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestRecipeRetrieveSerializer:
    def test_can_return_secondary_picture(self):
        recipe = RecipeFactory.create()
        with open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb') as f:
            recipe.secondary_picture = SimpleUploadedFile(
                name='recipe.jpg',
                content=f.read(),
                content_type='image/jpeg'
            )
            recipe.save()

        serializer = RecipeRetrieveSerializer()

        assert 'medium' in serializer.get_secondary_picture_thumbs(recipe)
        assert 'large' in serializer.get_secondary_picture_thumbs(recipe)


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
                'composition': [
                    {
                        'ingredients': [
                            {
                                'ingredient': 'Eau',
                            },
                            {
                                'ingredient': 'Olives',
                                'quantity': 2,
                            },
                        ],
                    },
                    {
                        'name': 'Pâte',
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
        composition = recipe_data.pop('composition')
        for composition_item in composition:
            for ingredients_item in composition_item['ingredients']:
                ingredient_name = ingredients_item['ingredient']
                recipe_ingredient = (
                    RecipeIngredient.objects
                    .filter(ingredient__name=ingredient_name.lower())
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
                'composition': [
                    {
                        'ingredients': [
                            {
                                'ingredient': 'Eau',
                            },
                            {
                                'ingredient': 'Olives',
                                'quantity': 2,
                            },
                        ],
                    },
                    {
                        'name': 'Pâte',
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
        assert recipe_data['tags'][1].lower() in list(recipe.tags.values_list('name', flat=True))
        assert recipe_data['tags'][2].lower() in list(recipe.tags.values_list('name', flat=True))

    def test_can_returns_ingredients_information(self):
        unit = UnitFactory.create()
        recipe_ingredient = RecipeIngredientFactory.create(unit=unit)
        serializer = RecipeIngredientSerializer()
        assert serializer.get_ingredient(recipe_ingredient) == recipe_ingredient.ingredient.name
        assert serializer.get_unit(recipe_ingredient) == recipe_ingredient.unit.name

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


@pytest.mark.django_db
class TestRecipeCompositionSerializer:
    def test_cannot_validate_composition_without_one_ingredient_object(self):
        serializer = RecipeCompositionSerializer(data={
            'name': 'Great composition',
            'ingredients': [],
        })
        assert not serializer.is_valid()
        assert 'ingredients' in serializer.errors
