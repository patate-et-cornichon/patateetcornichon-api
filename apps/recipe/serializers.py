from rest_framework import serializers

from apps.recipe.models import Category, Recipe


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
            'children'
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


class RecipeCreateUpdateSerializer(BaseRecipeSerializer):
    """ This serializer is used to create or update Recipe models. """

    default_error_messages = {
        'steps_required': 'At least one step is required.',
    }

    def validate_steps(self, value):
        """ At least one step is required. """
        if not value:  # pragma: no cover
            return self.fail('steps_required')
        return value
