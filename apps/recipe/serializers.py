from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify
from rest_framework import serializers

from apps.comment.models import Comment
from common.drf.fields import Base64ImageField

from .models import Category, Ingredient, Recipe, RecipeComposition, RecipeIngredient, Tag, Unit


class ChildCategorySerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with child categories instances. """

    class Meta:
        model = Category
        fields = (
            'id',
            'slug',
            'name',
        )
    read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with categories instances. """

    children = ChildCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
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


class IngredientSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with ingredients instances. """

    class Meta:
        model = Ingredient
        fields = (
            'slug',
            'name',
        )


class UnitSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with units instances. """

    class Meta:
        model = Unit
        fields = (
            'name',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with recipe ingredients instances. """

    ingredient = serializers.CharField(max_length=255)
    unit = serializers.CharField(max_length=255, required=False, allow_null=True)

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


class RecipeCompositionSerializer(serializers.ModelSerializer):
    """ This is the base serializer of Recipe Composition serializers. """

    ingredients = RecipeIngredientSerializer(many=True)

    default_error_messages = {
        'ingredients_required': 'At least one ingredient is required.',
    }

    class Meta:
        model = RecipeComposition
        fields = (
            'name',
            'ingredients',
        )

    def validate_ingredients(self, value):
        """ At least one ingredient is required. """
        if not value:
            return self.fail('ingredients_required')
        return value


class BaseRecipeSerializer(serializers.ModelSerializer):
    """ This is the base serializer of Recipe serializers. """

    composition = RecipeCompositionSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'slug',
            'published',
            'created',
            'updated',

            # Titles
            'title',
            'sub_title',
            'full_title',

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
            'composition',
            'steps',

            # SEO
            'meta_description',
        )
        read_only_fields = ('id', 'updated')


class RecipeRetrieveSerializer(BaseRecipeSerializer):
    """ This serializer is used to retrieve Recipe instances. """

    main_picture_thumbs = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta(BaseRecipeSerializer.Meta):
        fields = BaseRecipeSerializer.Meta.fields + (
            'comments_count',
            'main_picture_thumbs',
            'secondary_picture_thumbs',
        )

    def get_comments_count(self, obj):
        """ Return the number of comments associated to the recipe. """
        comments = Comment.objects.filter(object_id=obj.id)
        return comments.count()

    def get_main_picture_thumbs(self, obj):
        """ Return the main picture large thumbnail. """
        return obj.main_picture_thumbs

    def get_secondary_picture_thumbs(self, obj):
        """ Return the secondary picture large thumbnail. """
        return obj.secondary_picture_thumbs


class RecipeCreateUpdateSerializer(BaseRecipeSerializer):
    """ This serializer is used to create or update Recipe instances. """

    created = serializers.DateTimeField(required=False)
    main_picture = Base64ImageField(max_length=None, write_only=True)
    secondary_picture = Base64ImageField(
        max_length=None,
        write_only=True,
        required=False,
        allow_null=True,
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
        allow_null=True,
    )

    default_error_messages = {
        'steps_required': 'At least one step is required.',
        'composition_required': 'At least one composition is required.',
    }

    class Meta(BaseRecipeSerializer.Meta):
        fields = BaseRecipeSerializer.Meta.fields + (
            'main_picture',
            'secondary_picture',
        )

    def validate_steps(self, value):
        """ At least one step is required. """
        if not value:  # pragma: no cover
            return self.fail('steps_required')
        return value

    def validate_composition(self, value):
        """ At least one composition is required. """
        if self.instance is None and not value:  # pragma: no cover
            return self.fail('composition_required')
        return value

    @transaction.atomic
    def save(self, **kwargs):
        """ Override the default save method."""
        composition = self.validated_data.pop('composition', None)
        tags = self.validated_data.pop('tags', None)

        # Save the new recipe
        instance = super().save(**kwargs)

        # Assign ingredients. For each ingredient, create it if not exists.
        if composition:
            instance.composition.clear()
            for item in composition:
                ingredients = []
                for recipe_ingredient_item in item['ingredients']:
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
                            name=ingredient_name.lower(),
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

                    ingredients.append(recipe_ingredient)

                # Add the composition to the recipe
                composition = RecipeComposition.objects.create(
                    name=item.get('name') or None,
                )
                composition.ingredients.set(ingredients)
                instance.composition.add(composition)

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
                    tag = Tag.objects.create(slug=tag_slug, name=tag_name.lower())
                instance.tags.add(tag)
