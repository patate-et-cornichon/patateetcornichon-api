import os
import shutil

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient


MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '.media')


@pytest.fixture(autouse=True)
def setup():
    settings.MEDIA_ROOT = MEDIA_ROOT


@pytest.yield_fixture(scope='session', autouse=True)
def teardown():
    yield
    if os.path.exists(MEDIA_ROOT):
        shutil.rmtree(MEDIA_ROOT)


class TestMainView:
    def test_can_return_mysterious_message(self):
        client = APIClient()
        response = client.get(reverse('main'))
        assert response.status_code == 200
