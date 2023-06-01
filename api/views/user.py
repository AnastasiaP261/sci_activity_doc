from django.core.exceptions import BadRequest
from django.http import Http404
from rest_framework import generics, permissions

import api.serializers.user
from api import serializers
from api.pagination import StandardResultsSetPagination
from auth_wrapper.license import IsOwnerObjectOrIsProfessorOrReadOnly
from core.models import User


class ResearcherList(generics.ListAPIView):
    """
    Список исследователей, отсортированных по ФИО.
    В конце списка будут присутствовать "архивные" пользователи.
    """
    serializer_class = api.serializers.user.UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]

    def get_queryset(self):
        try:
            if 'rsrch_id' in self.request.query_params:
                rsrch_id = int(self.request.query_params['rsrch_id'])
                queryset = User.objects. \
                    filter(is_superuser=False, research=rsrch_id). \
                    order_by('-is_active', 'last_name', 'first_name', 'surname')
                return queryset

            if 'user_ids' in self.request.query_params:
                user_ids = self.request.query_params['user_ids']
                user_ids = (int(id) for id in user_ids.split('|'))
                queryset = User.objects. \
                    filter(is_superuser=False, id__in=user_ids). \
                    order_by('-is_active', 'last_name', 'first_name', 'surname')
                return queryset

            queryset = User.objects. \
                filter(is_superuser=False). \
                order_by('-is_active', 'last_name', 'first_name', 'surname')
            return queryset

        except User.DoesNotExist:
            raise Http404()
        except KeyError:
            raise BadRequest


class UserDetail(generics.RetrieveAPIView):
    """
    Текущий пользователь
    """
    serializer_class = api.serializers.user.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_object(self):
        try:
            return User.objects.get(username=self.request.user.get_username())
        except User.DoesNotExist:
            raise Http404()
