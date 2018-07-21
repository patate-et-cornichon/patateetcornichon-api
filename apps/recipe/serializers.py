from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify
from rest_framework import serializers

from .models import Category, Recipe, Tag


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


class BaseRecipeSerializer(serializers.ModelSerializer):
    """ This is the base serializer of Recipe serializers. """

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

    tags = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        write_only=True,
    )

    default_error_messages = {
        'steps_required': 'At least one step is required.',
    }

    def validate_steps(self, value):
        """ At least one step is required. """
        if not value:  # pragma: no cover
            return self.fail('steps_required')
        return value

    @transaction.atomic
    def save(self, **kwargs):
        """ Override the default save method."""
        tags = self.validated_data.pop('tags', None)

        # Save the new recipe
        instance = super().save(**kwargs)

        # Assign tags. For each tag, create it if not exists.
        if tags is not None:
            instance.tags.clear()

            for tag_name in tags:
                tag_slug = slugify(tag_name)
                tag = (
                    Tag.objects
                    .filter(Q(slug=tag_slug) | Q(name=tag_name))
                    .first()
                )
                if tag is None:
                    tag = Tag.objects.create(slug=tag_slug, name=tag_name)
                instance.tags.add(tag)
