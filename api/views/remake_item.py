import collections
import json

from django.core.exceptions import BadRequest
from django.db import transaction
from django.http import Http404
from rest_framework import generics, permissions
from rest_framework.response import Response

from api import serializers
from sci_activity_doc.consts import GET_METHOD, DELETE_METHOD, PATCH_METHOD
from sci_activity_doc.settings import REMAKE_ITEMS_LISTS_CACHE_TIME
from auth_wrapper.license import IsOwnerObjectOrIsProfessorOrReadOnly
from core.models import Graph, NodesNotesRelation, Note
from latex2html.models import RemakeItem
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from api.pagination import StandardResultsSetPagination


class RemakeItemDetail(generics.UpdateAPIView,
                       generics.DestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated, ]
    permission_classes = []
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
    serializer_class = serializers.RemakeItemSerializer

    def get_object(self):
        try:
            id = self.kwargs.get(self.lookup_url_kwarg, '')
            item = RemakeItem.objects.get(pk=id)

            return item
        except (RemakeItem.DoesNotExist):
            raise Http404()

class RemakeItemList(generics.ListAPIView,
                     generics.CreateAPIView):
    # permission_classes = [permissions.IsAuthenticated, ]
    permission_classes = []
    serializer_class = serializers.RemakeItemSerializer
    pagination_class = StandardResultsSetPagination
    queryset = RemakeItem.objects.all()

    @method_decorator(cache_page(REMAKE_ITEMS_LISTS_CACHE_TIME))  # будет закешировано на столько секунд
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
