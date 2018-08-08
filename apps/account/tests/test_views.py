import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import User


@pytest.mark.django_db
class TestUserViewSet:
    def test_can_create_a_new_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }

        client = APIClient()
        response = client.post(reverse('account:user-list'), user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.filter(email=user_data['email']).first()

        assert user is not None
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.password != user_data['password']

    def test_can_retrieve_all_users_when_admin(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_superuser(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('account:user-list'))

        assert response.status_code == status.HTTP_200_OK
        assert user_data['email'] == response.data[0]['email']

    def test_cannot_retrieve_self_user_data(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_user(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('account:user-detail', kwargs={'pk': user.id}))

        assert response.status_code == status.HTTP_200_OK

    def test_cannot_retrieve_all_users_when_not_logged(self):
        client = APIClient()
        response = client.get(reverse('account:user-list'))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_retrieve_all_users_when_normal_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_user(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('account:user-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_access_to_others_data_for_non_admin_users(self):
        user_1_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user_2_data = {
            'email': 'test2@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        User.objects.create_user(**user_1_data)
        other_user = User.objects.create_user(**user_2_data)

        client = APIClient()
        client.login(username=user_1_data['email'], password=user_1_data['password'])
        response = client.get(reverse('account:user-detail', kwargs={'pk': other_user.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN
