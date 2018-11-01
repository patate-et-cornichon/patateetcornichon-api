from rest_framework import serializers


class MailChimpSerializer(serializers.Serializer):
    email = serializers.EmailField()
