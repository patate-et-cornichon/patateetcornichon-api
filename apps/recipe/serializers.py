from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify
from rest_framework import serializers

from common.drf.fields import Base64ImageField

from .models import Category, Ingredient, Recipe, RecipeIngredient, Tag, Unit


class ChildCategorySerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with child categories instances. """

    class Meta:
        model = Category
        fields = (
            'id',
            'slug',
            'name',
        )


class CategorySerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with categories instances. """

    children = ChildCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'slug',
            'name',
            'children',
        )


class TagSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with tags instances. """

    class Meta:
        model = Tag
        fields = (
            'slug',
            'name',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with recipe ingredients instances. """

    ingredient = serializers.CharField(max_length=255)
    unit = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = RecipeIngredient
        fields = (
            'ingredient',
            'quantity',
            'unit',
        )

    def get_ingredient(self, obj):
        return obj.ingredient.name

    def get_unit(self, obj):
        return obj.unit.name


class BaseRecipeSerializer(serializers.ModelSerializer):
    """ This is the base serializer of Recipe serializers. """

    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'slug',

            # Titles
            'title',
            'sub_title',
            'full_title',

            # Pictures
            'main_picture',
            'secondary_picture',

            # Recipe meta
            'goal',
            'preparation_time',
            'cooking_time',
            'fridge_time',
            'leavening_time',
            'difficulty',

            # Categories and tags
            'categories',
            'tags',

            # Recipe content
            'introduction',
            'ingredients',
            'steps',

            # SEO
            'meta_description',
        )
        read_only_fields = ('id',)


class RecipeRetrieveSerializer(BaseRecipeSerializer):
    """ This serializer is used to retrieve Recipe models. """

    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeCreateUpdateSerializer(BaseRecipeSerializer):
    """ This serializer is used to create or update Recipe models. """

    main_picture = Base64ImageField(max_length=None, write_only=True)
    secondary_picture = Base64ImageField(
        max_length=None,
        write_only=True,
        required=False,
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        write_only=True,
    )

    default_error_messages = {
        'steps_required': 'At least one step is required.',
        'ingredients_required': 'At least one ingredient step is required.',
    }

    def validate_steps(self, value):
        """ At least one step is required. """
        if not value:  # pragma: no cover
            return self.fail('steps_required')
        return value

    def validate_ingredients(self, value):
        """ At least one ingredients is required. """
        if self.instance is None and not value:  # pragma: no cover
            return self.fail('ingredients_required')
        return value

    @transaction.atomic
    def save(self, **kwargs):
        """ Override the default save method."""
        ingredients = self.validated_data.pop('ingredients', None)
        tags = self.validated_data.pop('tags', None)

        # Save the new recipe
        instance = super().save(**kwargs)

        # Assign ingredients. For each ingredient, create it if not exists.
        if ingredients:
            instance.ingredients.clear()
            for recipe_ingredient_item in ingredients:
                # Ingredient management
                ingredient_name = recipe_ingredient_item['ingredient']
                ingredient_slug = slugify(ingredient_name)
                ingredient = (
                    Ingredient.objects
                    .filter(Q(slug=ingredient_slug) | Q(name__iexact=ingredient_name))
                    .first()
                )
                if ingredient is None:
                    ingredient = Ingredient.objects.create(
                        slug=ingredient_slug,
                        name=ingredient_name,
                    )

                # Ingredient Unit management
                unit_name = recipe_ingredient_item.get('unit')
                unit = None
                if unit_name is not None:
                    unit, _ = Unit.objects.get_or_create(
                        name__iexact=unit_name,
                        defaults={'name': unit_name},
                    )

                recipe_ingredient = RecipeIngredient.objects.create(
                    ingredient=ingredient,
                    unit=unit,
                    quantity=recipe_ingredient_item.get('quantity'),
                )

                instance.ingredients.add(recipe_ingredient)

        # Assign tags. For each tag, create it if not exists.
        if tags is not None:
            instance.tags.clear()

            for tag_name in tags:
                tag_slug = slugify(tag_name)
                tag = (
                    Tag.objects
                    .filter(Q(slug=tag_slug) | Q(name__iexact=tag_name))
                    .first()
                )
                if tag is None:
                    tag = Tag.objects.create(slug=tag_slug, name=tag_name)
                instance.tags.add(tag)
