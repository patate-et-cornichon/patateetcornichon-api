import os
from base64 import b64encode

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recipe.models import Recipe, RecipeIngredient, RecipeSelection
from apps.recipe.serializers import (
    RecipeCompositionSerializer, RecipeCreateUpdateSerializer, RecipeIngredientSerializer,
    RecipeSelectionCreateUpdateSerializer, RecipeSelectionRetrieveSerializer)
from apps.recipe.tests.factories import (
    CategoryFactory, RecipeFactory, RecipeIngredientFactory, RecipeSelectionFactory,
    SelectedRecipeFactory, TagFactory, UnitFactory)


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


@pytest.mark.django_db
class TestRecipeSelectionRetrieveSerializer:
    def test_can_return_recipes_respecting_order(self):
        selection = RecipeSelectionFactory.create()
        selected_recipe_1 = SelectedRecipeFactory(
            order=1,
            selection=selection,
        )
        selected_recipe_2 = SelectedRecipeFactory(
            order=2,
            selection=selection,
        )

        serializer = RecipeSelectionRetrieveSerializer(instance=selection)
        recipes = serializer.data['recipes']
        assert recipes[0]['id'] == str(selected_recipe_1.recipe.id)
        assert recipes[1]['id'] == str(selected_recipe_2.recipe.id)


@pytest.mark.django_db
class TestRecipeSelectionCreateUpdateSerializer:
    def test_cannot_create_a_selection_instance_if_no_recipe(self):
        selection_data = {
            'slug': 'super-selection',
            'title': 'Noël',
            'picture': SimpleUploadedFile(
                name='recipe.jpg',
                content=open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb').read(),
                content_type='image/jpeg'
            ),
            'recipes': [],
            'description': 'Hello world',
            'meta_description': 'Recettes de crêpes vegan',
        }

        serializer = RecipeSelectionCreateUpdateSerializer(data=selection_data)
        assert not serializer.is_valid()
        assert 'recipes' in serializer.errors

    def test_cannot_associate_related_recipes(self):
        recipe_1 = RecipeFactory.create()
        recipe_2 = RecipeFactory.create()
        selection_data = {
            'slug': 'super-selection',
            'title': 'Noël',
            'picture': SimpleUploadedFile(
                name='recipe.jpg',
                content=open(os.path.join(FIXTURE_ROOT, 'recipe.jpg'), 'rb').read(),
                content_type='image/jpeg'
            ),
            'recipes': [
                {
                    'recipe': recipe_1.id,
                    'order': 1,
                },
                {
                    'recipe': recipe_2.id,
                    'order': 2,
                },
            ],
            'description': 'Hello world',
            'meta_description': 'Recettes de crêpes vegan',
        }

        serializer = RecipeSelectionCreateUpdateSerializer(data=selection_data)
        assert serializer.is_valid()

        serializer.save()

        selection = RecipeSelection.objects.filter(slug='super-selection').first()
        assert selection is not None

        assert list(selection.recipes.all()) == [recipe_2, recipe_1]
