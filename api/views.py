from typing import Any

from rest_framework import viewsets, mixins, generics, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render

from .serializers import UserSerializer
from user.models import User


class StandardResultsSetPagination(PageNumberPagination):
    """
    Класс для настройки пагинации
    """
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'size'
    page_query_param = 'page'


class UserGetView(generics.ListAPIView):
    """
    Текущий пользователь
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(id=1)  # TODO: здесь должна быть инфа о текущем юзере


class ResearcherListView(generics.ListAPIView):
    """
    Список исследователей, отсортированных по ФИО. В конце списка будут присутствовать "архивные" пользователи.
    """
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    queryset = User.objects.filter(is_superuser=False).order_by('last_name', 'first_name', 'surname')
    # TODO: добавить сортировку по архивности
