from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from .serializers import CustomUserSerializer
from core.models import User
from rest_framework import permissions, generics


class StandardResultsSetPagination(PageNumberPagination):
    """
    Класс для настройки пагинации
    """
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'size'
    page_query_param = 'page'


class ResearcherListView(generics.ListAPIView):
    """
    Список исследователей, отсортированных по ФИО. В конце списка будут присутствовать "архивные" пользователи.
    """
    serializer_class = CustomUserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(is_superuser=False).order_by('-is_active', 'last_name', 'first_name', 'surname')


class UserGetView(generics.ListAPIView):
    """
    Текущий пользователь
    """
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.get_username())

    def get_object(self):
        return User.objects.get_by_natural_key(self.request.user.get_username())
