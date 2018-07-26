import pytest
from django.core.exceptions import ValidationError

from common.drf.fields import Base64ImageField


class TestBase64ImageField:
    def test_can_properly_process_a_base64_image(self):
        raw_img = ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADU'
                   'lEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg==')
        field = Base64ImageField()
        content_file = field.to_internal_value(raw_img)
        assert content_file.name.endswith('png')
        assert content_file.size

    def test_fails_if_the_image_cannot_be_processed(self):
        raw_img = 'data:image/png;base64,1231'
        field = Base64ImageField()
        with pytest.raises(ValidationError):
            field.to_internal_value(raw_img)
