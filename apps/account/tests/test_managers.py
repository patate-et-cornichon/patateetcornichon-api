import pytest

from apps.account.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_can_create_a_normal_user_and_encrypt_password(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_user(**user_data)

        assert user.password != user_data['password']

    @pytest.mark.xfail(raises=ValueError)
    def test_cannot_create_a_normal_user_without_email(self):
        user_data = {
            'email': None,
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_user(**user_data)

    def test_can_create_a_super_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_superuser(**user_data)

        assert user.password != user_data['password']
        assert user.is_staff
        assert user.is_superuser
