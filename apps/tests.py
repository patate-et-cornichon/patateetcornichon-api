from django.urls import reverse
from rest_framework.test import APIClient


class TestMainView:
    def test_can_return_mysterious_message(self):
        client = APIClient()
        response = client.get(reverse('main'))
        assert response.status_code == 200
