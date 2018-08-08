from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import User
from .permissions import IsAdminOrIsSelf
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['retrieve', 'partial_update']:
            permission_classes = [IsAdminOrIsSelf]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
