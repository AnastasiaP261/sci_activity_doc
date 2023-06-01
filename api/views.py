import collections
import json

from django.core.exceptions import ObjectDoesNotExist, BadRequest
from rest_framework.exceptions import ValidationError, NotFound
from auth_wrapper.license import IsOwnerObjectOrIsProfessorOrReadOnly, IsProfessorOrReadOnly

from builtins import Exception, KeyError
from django.db import transaction
from django.http import Http404
from rest_framework import permissions, generics, mixins, status
from rest_framework.response import Response

from core.models import User, Note, NodesNotesRelation, Graph, Research
from . import serializers
from .pagination import StandardResultsSetPagination

GET_METHOD = 'GET'
POST_METHOD = 'POST'
PATCH_METHOD = 'PATCH'
DELETE_METHOD = 'DELETE'


class ResearcherList(generics.ListAPIView):
    """
    Список исследователей, отсортированных по ФИО.
    В конце списка будут присутствовать "архивные" пользователи.
    """
    serializer_class = serializers.UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

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
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_object(self):
        try:
            return User.objects.get(username=self.request.user.get_username())
        except User.DoesNotExist:
            raise Http404()


class NoteDetail(generics.RetrieveAPIView,
                 generics.DestroyAPIView):
    lookup_url_kwarg = 'note_id'
    lookup_field = 'note_id'
    serializer_class = serializers.NoteWithAuthorInfoSerializer

    def get_permissions(self):
        permission_classes: list
        if self.request.method == GET_METHOD:
            permission_classes = [permissions.IsAuthenticated]

        if self.request.method == DELETE_METHOD:
            permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]

        return [permission() for permission in permission_classes]

    def get_object(self):
        try:
            note_id = int(self.kwargs.get(self.lookup_url_kwarg, 0))
            if self.request.method == GET_METHOD:
                notes = Note.objects.\
                    prefetch_related('user_id').\
                    get(note_id=note_id)
                nodes_notes_relations = NodesNotesRelation.objects.\
                    filter(note_id_id=note_id)

                return notes, nodes_notes_relations

            elif self.request.method == DELETE_METHOD:
                note = Note.objects.get(note_id=note_id)
                return note

        except Note.DoesNotExist:
            raise Http404()

    def get_serializer(self, *args, **kwargs):
        note_serializer = serializers.NoteWithAuthorInfoSerializer
        nnr_serializer = serializers.NodesNotesRelationSerializer

        kwargs.setdefault('context', self.get_serializer_context())
        return serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        notes, nnr = self.get_object()
        serializer = self.get_serializer(notes)

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

        # TODO: сюда добавить title и text заметки см. https://sa2systems.ru:88/help/api/repository_files.md

        return Response(serializer.data)

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
            pass  # TODO: здесь должно доставаться из латеха

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


class GraphDetail(generics.RetrieveAPIView,
                  generics.UpdateAPIView,
                  generics.DestroyAPIView):
    lookup_url_kwarg = 'graph_id'
    lookup_field = 'graph_id'

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

    def get_object(self):
        try:
            graph_id = int(self.kwargs.get(self.lookup_url_kwarg, 0))

            if self.request.method == GET_METHOD:
                graph = Graph.objects.get(graph_id=graph_id)
                nodes = NodesNotesRelation.objects.filter(graph_id=graph_id)

                return graph, nodes

            if self.request.method in (DELETE_METHOD, PATCH_METHOD):
                graph = Graph.objects.get(graph_id=graph_id)

                return graph

        except (Note.DoesNotExist, Graph.DoesNotExist, NodesNotesRelation.DoesNotExist):
            raise Http404()

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())

        if self.request.method == GET_METHOD:
            graph_serializer = serializers.GraphSerializer
            nodes_notes_rel_serializer = serializers.NodesNotesRelationSerializer

            return graph_serializer(*args, **kwargs), nodes_notes_rel_serializer(*args, **kwargs)

        elif self.request.method == PATCH_METHOD:
            title_serializer = serializers.GraphTitleUpdateSerializer
            metadata_serializer = serializers.GraphMetadataUpdateSerializer
            levels_serializer = serializers.GraphLevelsUpdateSerializer

            return title_serializer(*args, **kwargs), \
                metadata_serializer(*args, **kwargs), \
                levels_serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        graph, notes = self.get_object()

        graph_serializer, _ = self.get_serializer(graph)
        _, nodes_notes_rel_serializer = self.get_serializer(notes, many=True)
        graph = graph_serializer.data
        notes = nodes_notes_rel_serializer.data
        nodes_metadata = json.loads(graph['nodes_metadata'])

        map_node_id_to_notes_ids = collections.defaultdict(list)  # маппинг айдишек узлов на список айдишек заметок
        notes_id_without_graph = list()  # список айдишек заметок, не привязанных ни к какому графу
        for note in notes:
            note = dict(note)
            if 'node_id' not in note and 'note_id' in note:
                notes_id_without_graph.append(note['note_id'])
            map_node_id_to_notes_ids[note['node_id']].append(note['note_id'])

        full_nodes_info = dict()
        for id in nodes_metadata:
            full_nodes_info[id] = dict()

            full_nodes_info[id]['title'] = nodes_metadata[id].get('title', '')
            full_nodes_info[id]['is_subgraph'] = nodes_metadata[id].get('subgraph', 0) != 0
            full_nodes_info[id]['subgraph_graph_id'] = nodes_metadata[id].get('subgraph', 0)
            full_nodes_info[id]['notes_ids'] = map_node_id_to_notes_ids[id]

        graph['notes_without_graph'] = notes_id_without_graph
        graph['nodes_metadata'] = full_nodes_info
        graph['levels'] = json.loads(graph['levels'])

        return Response(graph)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        graph = self.get_object()
        title_serializer, metadata_serializer, levels_serializer = \
            self.get_serializer(graph, data=request.data, partial=partial)

        if 'title' in request.data and title_serializer.is_valid(raise_exception=True):
            serializer = title_serializer
        elif 'node_metadata' in request.data and metadata_serializer.is_valid(raise_exception=True):
            serializer = metadata_serializer
        elif 'levels' in request.data and levels_serializer.is_valid(raise_exception=True):
            serializer = levels_serializer
        else:
            raise BadRequest()

        super().perform_update(serializer)

        if getattr(graph, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            graph._prefetched_objects_cache = {}

        return Response(serializer.data)

    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        # по инструкциям CASCADE, здесь удалятся также записи всех связанных NodesNotesRelations
        return super().delete(request, *args, **kwargs)


class CreateGraph(generics.CreateAPIView):
    serializer_class = serializers.GraphSerializer


class NodeDetail(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated] TODO: включи
    serializer_class = serializers.NoteWithAuthorInfoSerializer

    def get_queryset(self):
        try:
            graph_id = int(self.kwargs.get('graph_id', 0))
            node_id = self.kwargs.get('node_id', '')

            obj = NodesNotesRelation.objects.filter(graph_id=graph_id, node_id=node_id).prefetch_related(
                'note_id').order_by('note_id__created_at')
            return obj
        except NodesNotesRelation.DoesNotExist:
            raise Http404()


class ResearchDetail(generics.RetrieveAPIView,
                     generics.UpdateAPIView,
                     generics.DestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated] TODO: включи
    lookup_url_kwarg = 'rsrch_id'

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    def get_object(self):
        try:
            rsrch_id = self.kwargs.get(self.lookup_url_kwarg, '')

            if self.request.method == GET_METHOD:
                research = Research.objects. \
                    get(pk=rsrch_id)
                graphs = Graph.objects. \
                    filter(rsrch_id=rsrch_id). \
                    order_by('title')
                notes_without_graph = Note.objects. \
                    filter(rsrch_id=rsrch_id, nodesnotesrelation__graph_id_id__isnull=True)

                return research, graphs, notes_without_graph

            elif self.request.method in (DELETE_METHOD, PATCH_METHOD):
                research = Research.objects. \
                    get(pk=rsrch_id)

                return research

            else:
                raise BadRequest()

        except (Note.DoesNotExist, Research.DoesNotExist, Graph.DoesNotExist):
            raise Http404()

    def get_serializer(self, *args, **kwargs):
        # для GET берем сериализаторы напрямую в retrieve, тк для них нужны разные аргументы

        if self.request.method == PATCH_METHOD:
            serializer = serializers.ResearchUpdateSerializer
            kwargs.setdefault('context', self.get_serializer_context())
            return serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        research, graphs, notes_without_graph = self.get_object()

        r_serialize = serializers.ResearchSerializer(research)
        research = r_serialize.data

        g_serializer = serializers.GraphTitleUpdateSerializer(graphs, many=True)
        graphs = g_serializer.data

        n_serializer = serializers.NoteWithoutGraphSerializer(notes_without_graph, many=True, required=False)
        notes_without_graph = n_serializer.data

        kwargs.setdefault('context', self.get_serializer_context())

        data = research
        data['graphs'] = graphs
        data['notes_without_graphs'] = notes_without_graph

        return Response(data)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        # по инструкциям CASCADE, здесь удалятся также записи всех связанных Graphs и NodesNotesRelations
        return super().destroy(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ResearchList(generics.CreateAPIView,
                   generics.ListAPIView):
    pagination_class = StandardResultsSetPagination

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

    def get_serializer(self, *args, **kwargs):
        if self.request.method == GET_METHOD:
            serializer = serializers.ResearchSerializer
        elif self.request.method == POST_METHOD:
            serializer = serializers.ResearchCreateSerializer
        else:
            raise BadRequest()

        kwargs.setdefault('context', self.get_serializer_context())
        return serializer(*args, **kwargs)

    def get_queryset(self):
        try:
            if 'user_id' in self.request.query_params:
                user_id = int(self.request.query_params['user_id'])
                queryset = Research.objects. \
                    filter(researchers__id=user_id). \
                    order_by('-created_at')

                return queryset

            queryset = Research.objects. \
                order_by('-created_at')
            return queryset

        except Research.DoesNotExist:
            raise Http404()
