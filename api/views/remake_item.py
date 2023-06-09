from django.http import Http404
from rest_framework import generics, permissions

from api import serializers
from api.pagination import StandardResultsSetPagination
from latex2html.models import RemakeItem


class RemakeItemDetail(generics.UpdateAPIView,
                       generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
    serializer_class = serializers.RemakeItemSerializer

    def get_object(self):
        try:
            id = self.kwargs.get(self.lookup_url_kwarg, '')
            item = RemakeItem.objects.get(pk=id)

            return item
        except RemakeItem.DoesNotExist:
            raise Http404()


class RemakeItemList(generics.ListAPIView,
                     generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = serializers.RemakeItemSerializer
    pagination_class = StandardResultsSetPagination
    queryset = RemakeItem.objects.all()
