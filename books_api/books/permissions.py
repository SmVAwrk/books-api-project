from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """Кастомные права доступа (любые методы для админа или владельца, для остальных только чтение)"""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and (request.user == obj.owner or request.user.is_staff)
        )


class IsOwnerOrAdmin(BasePermission):
    """Кастомные права доступа (доступ только для админа и владельца)"""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.is_authenticated and (request.user == obj.owner or request.user.is_staff)
        )


class IsAdminOrOwnerReadOnly(BasePermission):
    """Кастомные права доступа (Любые методы для админа, для владельца только чтение)"""

    def has_object_permission(self, request, view, obj):
        return bool(
            (request.method in SAFE_METHODS and request.user == obj.user) or
            request.user and
            request.user.is_authenticated and request.user.is_staff
        )


class IsAdminOrReadOnly(BasePermission):
    """Кастомные права доступа (Любые методы для админа, для остальных только чтение)"""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and request.user.is_staff
        )
