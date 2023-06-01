from rest_framework.permissions import BasePermission, SAFE_METHODS

ADMIN_GROUP = 'admin'
PROFESSOR_GROUP = 'professor'
RESEARCHER_GROUP = 'researcher'


class IsOwnerObjectOrIsProfessorOrReadOnly(BasePermission):
    """
    Проверяем, является ли пользователь привязанным к исследованию или преподавателем.
    Это гарантирует, что исследователь и преподаватели - единственные, кто может изменить данные исследования.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        is_owner = request.user.id in obj.get_user_ids()

        is_prof = False
        for g in request.user.get_groups_list():
            if g in (PROFESSOR_GROUP, ADMIN_GROUP):
                is_prof = True

        return is_owner or is_prof


class IsProfessorOrReadOnly(BasePermission):
    """
    Доступ к некоторым небезопасным методам может иметь только преподаватель
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        have_access = False
        for g in request.user.get_groups_list():
            if g in (PROFESSOR_GROUP, ADMIN_GROUP):
                have_access = True

        return have_access
