import pytest

from apps.account.models import User
from apps.account.permissions import IsAdminOrIsSelf


@pytest.mark.django_db
class TestIsAdminOrIsSelf:
    def test_can_have_permission_to_access_other_user_data_for_staff_user(self, rf):
        user_data_1 = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user_data_2 = {
            'email': 'test2@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user_1 = User.objects.create_superuser(**user_data_1)
        user_2 = User.objects.create_user(**user_data_2)

        request = rf.get('/')
        request.user = user_1

        permission = IsAdminOrIsSelf()

        assert permission.has_object_permission(request, object(), user_2)

    def test_can_have_permission_to_access_other_user_data_for_self_user(self, rf):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_superuser(**user_data)

        request = rf.get('/')
        request.user = user

        permission = IsAdminOrIsSelf()

        assert permission.has_object_permission(request, object(), user)

    def test_cannot_have_permission_to_access_other_user_data_for_normal_user(self, rf):
        user_data_1 = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user_data_2 = {
            'email': 'test2@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user_1 = User.objects.create_user(**user_data_1)
        user_2 = User.objects.create_user(**user_data_2)

        request = rf.get('/')
        request.user = user_1

        permission = IsAdminOrIsSelf()

        assert not permission.has_object_permission(request, object(), user_2)
