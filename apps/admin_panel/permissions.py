"""
Custom permissions for the admin panel.
All admin API endpoints require the user to be authenticated AND is_staff=True.
"""

from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """
    Allows access only to users with is_staff=True.
    Returns 403 (not 404) so the frontend can distinguish
    'not authorised' from 'not found'.
    """
    message = "You do not have permission to access the admin panel."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
