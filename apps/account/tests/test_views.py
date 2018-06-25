import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.account.models import User


@pytest.mark.django_db
class TestUserViewSet:
    def test_can_create_a_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
        }

        client = APIClient()
        response = client.post(reverse('account:user-list'), user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.filter(email=user_data['email']).first()

        assert user is not None
        assert user.email == user_data['email']
        assert user.password != user_data['password']

    def test_can_retrieve_all_users_when_admin(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
        }
        User.objects.create_superuser(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('account:user-list'))

        assert response.status_code == status.HTTP_200_OK
        assert user_data['email'] == response.data[0]['email']

    def test_cannot_retrieve_all_users_when_not_logged(self):
        client = APIClient()
        response = client.get(reverse('account:user-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_retrieve_all_users_when_normal_user(self):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
        }
        User.objects.create_user(**user_data)

        client = APIClient()
        client.login(username=user_data['email'], password=user_data['password'])
        response = client.get(reverse('account:user-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN
