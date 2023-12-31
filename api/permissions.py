from rest_framework import permissions


class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user and request.user.is_staff) or (obj.user == request.user)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user)

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
