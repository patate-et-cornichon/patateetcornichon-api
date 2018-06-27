import pytest

from apps.account.models import User
from apps.account.serializers import UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    def test_can_create_a_new_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
        }

        serializer = UserSerializer(data=user_data)
        assert serializer.is_valid()

        serializer.save()

        user = User.objects.filter(email=user_data['email']).first()
        assert user is not None
        assert user.email == user_data['email']
        assert user.password != user_data['password']

    def test_can_update_an_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
        }
        user = User.objects.create_user(**user_data)

        new_user_data = {
            'email': 'test2@test.com',
            'password': 'toto',
            'first_name': 'Kevin'
        }

        serializer = UserSerializer(
            data=new_user_data,
            instance=user,
            partial=True,
        )
        assert serializer.is_valid()

        serializer.save()

        assert user.email == new_user_data['email']
        assert user.check_password(new_user_data['password'])
        assert user.first_name == new_user_data['first_name']
