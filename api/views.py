from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from . import serializers as s
from core.models import User, Note, NodesNotesRelation
from rest_framework import permissions, generics, mixins, status
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Класс для настройки пагинации
    """
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'size'
    page_query_param = 'page'


class ResearcherList(generics.ListAPIView):
    """
    Список исследователей, отсортированных по ФИО. В конце списка будут присутствовать "архивные" пользователи.
    """
    serializer_class = s.CustomUserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(is_superuser=False).order_by('-is_active', 'last_name', 'first_name', 'surname')


class UserDetail(generics.ListAPIView):
    """
    Текущий пользователь
    """
    serializer_class = s.CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.get_username())


class NoteDetail(generics.GenericAPIView,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin):
    serializer_class = s.NoteListSerializer
    lookup_url_kwarg = 'note_id'
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'note_id'

    def retrieve_get_object(self):
        try:
            note_id = int(self.kwargs.get(self.lookup_url_kwarg))
            data = NodesNotesRelation.objects.prefetch_related('note_id__user_id').get(note_id=note_id)
            return data
        except Note.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        instance = self.retrieve_get_object()
        serializer = self.get_serializer(instance)

        data = serializer.data
        if data['author']['surname']:
            data['author']['full_name'] = \
                f"{data['author']['last_name']} {data['author']['first_name'][0]}.{data['author']['surname'][0]}."
        else:
            data['author']['full_name'] = \
                f"{data['author']['last_name']} {data['author']['first_name'][0]}."

        data['author'].pop('surname')
        data['author'].pop('first_name')
        data['author'].pop('last_name')

        # TODO: сюда добавить title и text заметки см. https://sa2systems.ru:88/help/api/repository_files.md

        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # def put(self, request, *args, **kwargs):
    #     # TODO: обновление заметки не готово
    #     return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        note_id = int(self.kwargs.get(self.lookup_url_kwarg))

        NodesNotesRelation.objects.filter(note_id=note_id).delete()
        Note.objects.get(note_id=note_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
