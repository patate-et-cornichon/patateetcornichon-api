import os
import shutil
import unittest.mock

import pytest
from django.conf import settings as settings

from apps.account.models import User
from apps.account.serializers import UserSerializer
from common.avatar import generate_avatar_name


FIXTURE_ROOT = os.path.join(settings.BASE_DIR, '../common/tests/fixtures')
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '.media')


@pytest.mark.django_db
class TestUserSerializer:
    @pytest.fixture(autouse=True)
    def setup(self):
        settings.MEDIA_ROOT = MEDIA_ROOT

    @pytest.yield_fixture(scope='session', autouse=True)
    def teardown(self):
        yield
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

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

    @unittest.mock.patch('requests.get')
    def test_can_save_an_user_avatar_on_accout_creation(self, mocked_get):
        with open(os.path.join(FIXTURE_ROOT, 'cartman.jpg'), 'rb') as f:
            mocked_get.return_value = unittest.mock.Mock(
                status_code=200,
                content=f.read(),
            )

        user_data = {
            'email': 'test@test.com',
            'password': 'test',
        }

        serializer = UserSerializer(data=user_data)
        assert serializer.is_valid()

        serializer.save()

        user = User.objects.filter(email=user_data['email']).first()
        assert user is not None
        assert user.avatar is not None
        assert generate_avatar_name('test@test.com', '.jpg') in user.avatar.name
