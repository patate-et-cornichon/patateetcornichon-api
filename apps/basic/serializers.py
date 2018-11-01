from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    """ Serializer used to contact Patate & Cornichon. """

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    content = serializers.CharField()


class MailChimpSerializer(serializers.Serializer):
    """ Serializer used to create a subscriber. """

    email = serializers.EmailField()
