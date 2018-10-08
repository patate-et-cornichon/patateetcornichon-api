from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify
from rest_framework import serializers

from apps.account.serializers import UserSerializer
from apps.comment.models import Comment
from common.drf.fields import Base64ImageField

from .models import Story, Tag


class TagSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with tags instances. """

    class Meta:
        model = Tag
        fields = (
            'slug',
            'name',
        )


class BaseStorySerializer(serializers.ModelSerializer):
    """ This is the base serializer of Recipe serializers. """

    class Meta:
        model = Story
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

            # Tags
            'tags',

            # Author
            'authors',

            # Story content
            'content',

            # SEO
            'meta_description',
        )
        read_only_fields = ('id', 'created', 'updated')


class StoryRetrieveSerializer(BaseStorySerializer):
    """ This serializer is used to retrieve Story instances. """

    main_picture_thumbs = serializers.SerializerMethodField()
    authors = UserSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta(BaseStorySerializer.Meta):
        fields = BaseStorySerializer.Meta.fields + (
            'comments_count',
            'main_picture_thumbs',
        )

    def get_comments_count(self, obj):
        """ Return the number of comments associated to the recipe. """
        comments = Comment.objects.filter(object_id=obj.id)
        return comments.count()

    def get_main_picture_thumbs(self, obj):
        """ Return the main picture large thumbnail. """
        return obj.main_picture_thumbs


class StoryCreateUpdateSerializer(BaseStorySerializer):
    """ This serializer is used to create or update Story instances. """

    main_picture = Base64ImageField(max_length=None, write_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
    )

    class Meta(BaseStorySerializer.Meta):
        fields = BaseStorySerializer.Meta.fields + (
            'main_picture',
        )

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
                    .filter(Q(slug=tag_slug) | Q(name__iexact=tag_name))
                    .first()
                )
                if tag is None:
                    tag = Tag.objects.create(slug=tag_slug, name=tag_name)
                instance.tags.add(tag)
