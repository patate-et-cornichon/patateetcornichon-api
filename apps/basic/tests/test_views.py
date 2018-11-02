import json
import unittest.mock

from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient


class TestContactView:
    def test_can_send_a_contact_email_message(self):
        data = {
            'name': 'Test',
            'email': 'test@test.com',
            'subject': 'Test',
            'content': 'Test',
        }

        client = APIClient()
        response = client.post(
            reverse('basic:contact'),
            data=json.dumps(data),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == data['subject']
        assert data['email'] in mail.outbox[0].reply_to

    def test_cannot_send_a_contact_email_message_with_invalid_data(self):
        data = {
            'name': 'Test',
            'email': 'test@test.com',
            'subject': 'Test',
        }

        client = APIClient()
        response = client.post(
            reverse('basic:contact'),
            data=json.dumps(data),
            content_type='application/json',
        )

        assert response.status_code == 400
        assert 'content' in response.json().keys()


class TestInstagramView:
    @unittest.mock.patch('requests.get')
    def test_can_return_data_from_instagram_api(self, mocked_get):
        mocked_response = unittest.mock.Mock()
        mocked_response.status_code = 200
        mocked_response.json.return_value = {
            'data': 'test',
        }
        mocked_get.return_value = mocked_response

        client = APIClient()
        response = client.get(
            reverse('basic:instagram'),
        )

        assert response.status_code == 200
        assert response.json() == 'test'

    @unittest.mock.patch('requests.get')
    def test_can_return_errors_from_instagram_api(self, mocked_get):
        mocked_response = unittest.mock.Mock()
        mocked_response.status_code = 400
        mocked_response.json.return_value = {
            'meta': {
                'error_message': 'test'
            },
        }
        mocked_get.return_value = mocked_response

        client = APIClient()
        response = client.get(
            reverse('basic:instagram'),
        )

        assert response.status_code == 400
        assert response.json()['detail'] == 'test'


class TestMailchimpView:
    @unittest.mock.patch('requests.post')
    def test_can_create_a_new_mailchimp_subscriber(self, mocked_post):
        mocked_response = unittest.mock.Mock()
        mocked_response.status_code = 200
        mocked_post.return_value = mocked_response

        data = {
            'email': 'test@test.com',
        }

        client = APIClient()
        response = client.post(
            reverse('basic:mailchimp'),
            data=json.dumps(data),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.json()['email'] == data['email']

    @unittest.mock.patch('requests.post')
    def test_can_return_error_from_mailchimp(self, mocked_post):
        mocked_response = unittest.mock.Mock()
        mocked_response.status_code = 400
        mocked_response.json.return_value = {
            'detail': 'test',
        }
        mocked_post.return_value = mocked_response

        data = {
            'email': 'test@test.com',
        }

        client = APIClient()
        response = client.post(
            reverse('basic:mailchimp'),
            data=json.dumps(data),
            content_type='application/json',
        )

        assert response.status_code == 400
        assert response.json()['detail'] == 'test'

    def test_cannot_create_subscriber_with_invalid_data(self):
        data = {
            'email': 'test',
        }

        client = APIClient()
        response = client.post(
            reverse('basic:mailchimp'),
            data=json.dumps(data),
            content_type='application/json',
        )

        assert response.status_code == 400
        assert 'email' in response.json().keys()
