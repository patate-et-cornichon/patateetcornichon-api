import base64
import uuid
from mimetypes import guess_extension

import magic
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """ Extends the ``serializers.ImageField`` to support base64 image uploads. """

    def to_internal_value(self, data):
        # Checks if we are considering a base64 string.
        if isinstance(data, str):
            # Check if the base64 string is in the "data:" format and breaks out the header from the
            # base64 content if this is applicable.
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            # Tries to decode the image file.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:  # pragma: no cover
                self.fail('invalid_image')

            # Generates a unique file name and determines the file extension.
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = f'{file_name}{file_extension}'

            data = ContentFile(decoded_file, name=complete_file_name)

        return super().to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        mime = magic.from_buffer(decoded_file, mime=True)
        extension = guess_extension(mime)
        extension = '.jpg' if extension == '.jpe' else extension
        return extension
