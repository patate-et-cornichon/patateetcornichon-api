from rest_framework import serializers

from apps.recipe.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with recipe instances. """

    default_error_messages = {
        'steps_required': 'At least one step is required.',
    }

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

            # Recipe content
            'introduction',
            'steps',

            # SEO
            'meta_description',
        )
        read_only_fields = ('id',)

    def validate_steps(self, value):
        """ At least one step is required. """
        if not value:
            return self.fail('steps_required')
        return value
