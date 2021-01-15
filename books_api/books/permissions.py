from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and (request.user == obj.owner or request.user.is_staff)
        )


class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.is_authenticated and (request.user == obj.owner or request.user.is_staff)
        )


class IsAdminOrOwnerReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (request.method in SAFE_METHODS and request.user == obj.user) or
            request.user and
            request.user.is_authenticated and request.user.is_staff
        )


class IsAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and request.user.is_staff
        )