import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


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
