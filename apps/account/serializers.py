from django.db import transaction
from django.templatetags.static import static
from rest_framework import serializers

from common.avatar import get_from_gravatar

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with user instances. """
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'is_staff',
            'email',
            'avatar',
            'password',
            'first_name',
            'last_name',
            'website',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        """ Create a new User instance. """
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']

        user = User.objects.create_user(email=email, first_name=first_name, password=password)

        # Try to get an avatar from the Gravatar service
        avatar = get_from_gravatar(email)
        if avatar is not None:
            path, file = avatar
            user.avatar.save(path, file, save=True)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        """ Update the User instance according to the validated data. """
        password = validated_data.pop('password', None)

        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

    def get_avatar(self, obj):
        """ Return the author avatar absolute uri or a default one. """
        avatar = obj.avatar
        if avatar:
            avatar_full_path = avatar.url
        else:
            avatar_index = len(obj.email) % 8 + 1
            avatar_full_path = static(f'comment/avatars/default_avatar_{avatar_index}.svg')
        request = self.context['request']
        avatar_absolute_uri = request.build_absolute_uri(avatar_full_path)
        return avatar_absolute_uri
