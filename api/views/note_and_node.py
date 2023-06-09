from django.core.exceptions import BadRequest
from django.db import transaction
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api import serializers
from api.pagination import StandardResultsSetPagination
from auth_wrapper.license import IsOwnerObjectOrIsProfessorOrReadOnly
from core.models import Note, Graph, NodesNotesRelation
from gitlab_client.client import GLClient, GitlabError
from gitlab_client.parse_url import parse_note_type_from_url
from latex2html.models import RemakeItem
from sci_activity_doc.consts import GET_METHOD, DELETE_METHOD
from sci_activity_doc.settings import NOTE_DETAIL_GET_CACHE_TIME
from sci_activity_doc.settings import REMAKE_LATEX2HTML_ENABLE


class NoteDetail(generics.RetrieveAPIView,
                 generics.DestroyAPIView,
                 GLClient):
    lookup_url_kwarg = 'note_id'
    lookup_field = 'note_id'
    serializer_class = serializers.NoteWithAuthorInfoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]

    def get_object(self):
        try:
            note_id = int(self.kwargs.get(self.lookup_url_kwarg, 0))
            if self.request.method == GET_METHOD:
                note = Note.objects. \
                    prefetch_related('user_id'). \
                    prefetch_related('nodesnotesrelation_set'). \
                    get(note_id=note_id)

            elif self.request.method == DELETE_METHOD:
                note = Note.objects.get(note_id=note_id)

            else:
                BadRequest()

            self.check_object_permissions(self.request, note)
            return note

        except Note.DoesNotExist:
            raise Http404()

    @method_decorator(cache_page(NOTE_DETAIL_GET_CACHE_TIME))  # будет закешировано на столько секунд
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        data = serializer.data
        if data['author']['surname']:
            data['author']['full_name'] = \
                f"{data['author']['last_name']} {data['author']['first_name'][0]}.{data['author']['surname'][0]}."
        else:
            data['author']['full_name'] = \
                f"{data['author']['last_name']} {data['author']['first_name'][0]}."

        data['author'].pop('surname', '')
        data['author'].pop('first_name', '')
        data['author'].pop('last_name', '')

        try:
            note_raw_text = self.get_note_raw_text_by_url(data['url'])
        except GitlabError as e:
            data['text'] = f'Не удалось получить текст заметки :(<br/>Проблемы с Gitlab: {e}'
        else:
            if REMAKE_LATEX2HTML_ENABLE:
                html_text = RemakeItem.objects.remake_latex_text(note_raw_text)
                data['text'] = html_text
            else:
                data['text'] = note_raw_text

        return Response(data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        # по инструкциям CASCADE, здесь удалятся также записи всех связанных NodesNotesRelations
        return super().destroy(request, *args, **kwargs)


class NoteCreate(generics.CreateAPIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]

    def get_serializer(self, *args, **kwargs):
        note_serializer = serializers.NoteSerializer
        nodes_notes_rel_serializer = serializers.NodesNotesRelationSerializer

        kwargs.setdefault('context', self.get_serializer_context())
        return note_serializer(*args, **kwargs), nodes_notes_rel_serializer(*args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        note_serializer, nodes_notes_rel_serializer = self.get_serializer(data=request.data)
        note_serializer.is_valid(raise_exception=True)
        note = note_serializer.data

        new_note = Note()
        new_note.url = note['url']
        new_note.rsrch_id_id = note['rsrch_id']
        new_note.user_id_id = request.user.id
        if 'note_type' in note:
            new_note.note_type = note['note_type']
        else:
            new_note.note_type = parse_note_type_from_url(note['url'])

        new_note.save()

        if 'graph_id' in request.data and 'node_id' in request.data:
            nodes_notes_rel_serializer.is_valid(raise_exception=True)
            nnr = nodes_notes_rel_serializer.data

            graph = Graph.objects.get(graph_id=nnr['graph_id'])
            if not graph.node_with_node_id_exists(str(nnr['node_id'])):
                raise ValidationError({"node_id": [f"Invalid pk {str(nnr['node_id'])} - object does not exist."]})

            notes_nodes_rel_data = NodesNotesRelation(
                graph_id_id=nnr['graph_id'],
                node_id=nnr['node_id'],
                note_id_id=new_note.note_id,
            )
            notes_nodes_rel_data.save()

            note_serializer.data['graph_id'] = nnr['graph_id']
            note_serializer.data['node_id'] = nnr['node_id']

        note_serializer.data['note_id'] = new_note.note_id

        headers = self.get_success_headers(note_serializer.data)
        return Response(note_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class NodeDetail(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]
    serializer_class = serializers.NoteWithoutGraphInfoSerializer

    def get_queryset(self):
        try:
            graph_id = int(self.kwargs.get('graph_id', 0))
            node_id = self.kwargs.get('node_id', '')

            notes = Note.objects. \
                prefetch_related('nodesnotesrelation_set'). \
                filter(nodesnotesrelation__graph_id_id=graph_id, nodesnotesrelation__node_id=node_id). \
                order_by('created_at')

            return notes

        except (NodesNotesRelation.DoesNotExist, Note.DoesNotExist):
            raise Http404()
