from rest_framework.response import Response
from rest_framework.views import APIView


class MainView(APIView):
    """ View just used to prove that the API exists. """

    def get(self, request, format=None):
        """ Returns a mysterious message. """
        content = 'That is not dead which can eternal lie, '
        content += 'And with strange aeons even death may die.'
        return Response(content)
