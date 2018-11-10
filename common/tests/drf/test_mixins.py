import unittest.mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from apps.account.models import User
from common.drf.mixins import CacheMixin


@pytest.mark.django_db
class TestCacheMixin:
    class MockedRetrieveListMixin:
        def retrieve(self):
            return

        def list(self):
            return

    class CacheView(CacheMixin, MockedRetrieveListMixin):
        def __init__(self, request):
            self.request = request

    @unittest.mock.patch('common.drf.mixins.cache_page', return_value=lambda x: x)
    def test_can_cache_retrieve_method_for_lambda_user(self, mocked_cache):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        view = self.CacheView(request)
        view.retrieve()
        assert mocked_cache.called

    @unittest.mock.patch('common.drf.mixins.cache_page', return_value=lambda x: x)
    def test_can_prevent_cache_retrieve_method_for_admin_user(self, mocked_cache):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_superuser(**user_data)
        request = RequestFactory().get('/')
        request.user = user

        view = self.CacheView(request)
        view.retrieve()
        assert not mocked_cache.called

    @unittest.mock.patch('common.drf.mixins.cache_page', return_value=lambda x: x)
    def test_can_cache_list_method_for_lambda_user(self, mocked_cache):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        view = self.CacheView(request)
        view.list()
        assert mocked_cache.called

    @unittest.mock.patch('common.drf.mixins.cache_page', return_value=lambda x: x)
    def test_can_prevent_cache_list_method_for_admin_user(self, mocked_cache):
        user_data = {
            'email': 'test@test.com',
            'password': 'test',
            'first_name': 'Toto',
        }
        user = User.objects.create_superuser(**user_data)
        request = RequestFactory().get('/')
        request.user = user

        view = self.CacheView(request)
        view.list()
        assert not mocked_cache.called
