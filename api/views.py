from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from .serializers import CustomUserSerializer
from auth_wrapper.models import User


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
    queryset = User.objects.filter(is_superuser=False).order_by('last_name', 'first_name', 'surname')
    # TODO: добавить сортировку по архивности
