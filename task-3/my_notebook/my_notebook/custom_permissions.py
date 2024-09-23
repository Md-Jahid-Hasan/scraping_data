from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = 'You are not allowed to perform this action'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.owner == request.user