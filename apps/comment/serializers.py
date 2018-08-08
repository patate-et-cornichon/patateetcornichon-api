from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.account.serializers import UnregisteredUserSerializer, UserSerializer
from apps.comment.constants import VALID_CONTENT_TYPES

from .models import Comment


class ChildCommentRetrieveSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with child categories instances. """

    class Meta:
        model = Comment
        fields = (
            'id',
            'is_valid',
            'registered_author',
            'unregistered_author',
            'be_notified',
            'content',
            'parent',
        )
        read_only_fields = ('id',)


class CommentRetrieveSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with Comment instances. """

    children = ChildCommentRetrieveSerializer(many=True, read_only=True, default=[])
    registered_author = UserSerializer(read_only=True)
    unregistered_author = UnregisteredUserSerializer(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field='app_label', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'is_valid',
            'registered_author',
            'unregistered_author',
            'be_notified',
            'content',
            'content_type',
            'object_id',
            'children',
        )
        read_only_fields = ('id',)


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """ This serializer is used to create or update Comment instances. """

    unregistered_author = UnregisteredUserSerializer(allow_null=True, required=False)
    content_type = serializers.ChoiceField(choices=VALID_CONTENT_TYPES)

    default_error_messages = {
        'object_invalid': 'The object does not exist.',
        'author_required': 'An author is required.',
    }

    class Meta:
        model = Comment
        fields = (
            'is_valid',
            'unregistered_author',
            'be_notified',
            'content',
            'content_type',
            'object_id',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        request = self.context['request']

        # Raise an error if no unregistered and user is not authenticated
        if not attrs.get('unregistered_author') and request.user.is_authenticated is False:
            return self.fail('author_required')

        return attrs

    def create(self, validated_data):
        request = self.context['request']

        content_type = validated_data.pop('content_type')
        object_id = validated_data.pop('object_id')
        is_valid = validated_data.get('is_valid')

        additional_data = {}

        if request.user.is_authenticated:
            additional_data['registered_author'] = request.user
        else:
            # Get or create unregistered user
            ...

        # Set is_valid attribute to False if request user is not staff
        if request.user.is_staff is False and is_valid:
            validated_data['is_valid'] = False

        # Get the content object and raise an error if not exists
        content_type_instance = ContentType.objects.get(model=content_type)
        try:
            additional_data['commented_object'] = content_type_instance.get_object_for_this_type(
                id=object_id,
            )
        except ObjectDoesNotExist:
            return self.fail('object_invalid')

        return super().create({**validated_data, **additional_data})
