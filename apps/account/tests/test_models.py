import pytest

from apps.account.models import User


@pytest.mark.django_db
class TestUser:
    def test_can_create_a_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Test',
            'last_name': 'Super Test',
        }
        user = User.objects.create(**user_data)

        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']
