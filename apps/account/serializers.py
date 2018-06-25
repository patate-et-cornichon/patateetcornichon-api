from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ This serializer is used to interact with user instances. """
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'website',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """ Create a new User instance. """
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create_user(email=email, password=password)
        return user

    def update(self, instance, validated_data):
        """ Update the User instance according to the validated data. """
        password = validated_data.pop('password', None)

        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
