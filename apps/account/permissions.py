from rest_framework.permissions import BasePermission


class IsAdminOrIsSelf(BasePermission):
    """
    Custom permission to only allow admin or owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """ Check if the user to retrieve is the current user.
            The user has permission only if he is admin or owner.
        """
        return obj == request.user or request.user.is_staff or request.user.is_superuser
