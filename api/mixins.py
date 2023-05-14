from rest_framework.response import Response


class ObjectModelMixin:
    """
    Один объект.
    """

    def object(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)
