from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import DefaultStorage
from rest_framework import serializers

from apps.account.serializers import UserSerializer
from apps.comment.constants import VALID_CONTENT_TYPES
from common.avatar import get_from_gravatar

from .models import Comment


class UnregisteredAuthorSerializer(serializers.Serializer):
    """ This serializer is used to represents an unregistered author referenced inside a
        ``Comment`` instance.
    """

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=255)
    avatar = serializers.SerializerMethodField()
    website = serializers.URLField(required=False, allow_null=True)

    def get_avatar(self, obj):
        """ Return the author avatar absolute uri. """
        avatar = obj.get('avatar')
        if avatar:
            fs = DefaultStorage()
            request = self.context['request']
            avatar_full_path = fs.url(avatar)
            avatar_absolute_uri = request.build_absolute_uri(avatar_full_path)
            return avatar_absolute_uri


class ChildCommentRetrieveSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with child categories instances. """

    registered_author = UserSerializer(read_only=True)
    unregistered_author = UnregisteredAuthorSerializer(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field='app_label', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'created',
            'updated',
            'is_valid',
            'registered_author',
            'unregistered_author',
            'be_notified',
            'content',
            'content_type',
            'object_id',
            'parent',
        )
        read_only_fields = ('id',)


class CommentRetrieveSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with Comment instances. """

    children = ChildCommentRetrieveSerializer(many=True, read_only=True, default=[])
    registered_author = UserSerializer(read_only=True)
    unregistered_author = UnregisteredAuthorSerializer(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field='app_label', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'created',
            'updated',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove children field if we are looking for all comments
        request = kwargs['context']['request']
        if 'object_id' not in request.GET:
            self.fields.pop('children')


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """ This serializer is used to create or update Comment instances. """

    unregistered_author = UnregisteredAuthorSerializer(required=False)
    content_type = serializers.ChoiceField(choices=VALID_CONTENT_TYPES)

    default_error_messages = {
        'object_invalid': 'The object does not exist.',
        'author_required': 'An author is required.',
    }

    class Meta:
        model = Comment
        fields = (
            'id',
            'is_valid',
            'unregistered_author',
            'be_notified',
            'content',
            'content_type',
            'object_id',
            'parent',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        request = self.context['request']

        # Raise an error if no unregistered and user is not authenticated
        if attrs.get('unregistered_author') is None and request.user.is_authenticated is False:
            return self.fail('author_required')

        return attrs

    def create(self, validated_data):
        request = self.context['request']

        content_type = validated_data.pop('content_type')
        object_id = validated_data.pop('object_id')
        unregistered_author = validated_data.pop('unregistered_author', None)
        is_valid = validated_data.get('is_valid')

        additional_data = {}

        # Set the comment user. Should be a registered author or an unregistered author.
        if request.user.is_authenticated:
            additional_data['registered_author'] = request.user
        else:
            additional_data['unregistered_author'] = dict(unregistered_author)

            # Fetch an avatar from Gravatar for the unregistered author
            unregistered_author_avatar = get_from_gravatar(unregistered_author['email'])
            if unregistered_author_avatar is not None:
                path, file = unregistered_author_avatar
                fs = DefaultStorage()
                filename = fs.save('avatars/' + path, file)
                additional_data['unregistered_author']['avatar'] = filename

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

        data = {**validated_data, **additional_data}
        return Comment.objects.create(**data)
