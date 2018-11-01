import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MailChimpSerializer


class InstagramView(APIView):
    """ View used to interact with Instagram API. """

    def get(self, request, format=None):
        """ Returns the Instagram media. """
        params = {
            'access_token': settings.INSTAGRAM_ACCESS_TOKEN,
            'count': request.query_params.get('count', 9),
        }
        response = requests.get(
            url='https://api.instagram.com/v1/users/self/media/recent/',
            params=params,
        )
        response_json = response.json()

        response_code = response.status_code
        if response_code != requests.codes.ok:
            return Response(
                data={
                    'detail': response_json['meta']['error_message'],
                },
                status=response_code,
            )
        return Response(response_json['data'])


class MailChimpSubscription(APIView):
    """ View allowing to manage Mailchimp subscriptions. """

    def post(self, request, format=None):
        """ Create a subscriber on a Mailchimp list. """
        serializer = MailChimpSerializer(data=request.data)

        if serializer.is_valid():
            subscriber_email = serializer.data['email']

            url = f'https://us10.api.mailchimp.com/3.0/lists/{settings.MAILCHIMP_LIST_ID}/members'
            auth = HTTPBasicAuth(settings.MAILCHIMP_USERNAME, settings.MAILCHIMP_API_KEY)
            data = {
                'email_address': subscriber_email,
                'status': 'subscribed'
            }

            response = requests.post(
                url=url,
                auth=auth,
                json=data,
            )
            response_json = response.json()

            response_code = response.status_code
            if response_code != requests.codes.ok:
                return Response(
                    data={
                        'detail': response_json['detail'],
                    },
                    status=response_code,
                )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
