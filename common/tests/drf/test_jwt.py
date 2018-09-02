import pytest

from apps.account.models import User
from common.drf.jwt import jwt_response_payload_handler


@pytest.mark.django_db
class TestJwtResponsePayloadHandler:
    def test_can_return_user_information(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Test',
            'last_name': 'Super Test',
        }
        user = User.objects.create(**user_data)

        jwt_response = jwt_response_payload_handler(token='test', user=user)

        assert jwt_response['user']['id'] == str(user.id)
