from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerProfileOrReadOnly(BasePermission):
    """
    Проверяем, похож ли запрашивающий пользователь на пользовательское поле объекта.
    Это гарантирует, что владелец профиля - единственный, кто может изменить свою информацию.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
