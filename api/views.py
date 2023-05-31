import collections
import json

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from . import serializers
from core.models import User, Note, NodesNotesRelation, Graph, Research
from rest_framework import permissions, generics, mixins, status
from rest_framework.response import Response
from django.db.models.signals import post_delete, pre_delete, post_save, pre_save, post_init, pre_init
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.db import transaction
from django.shortcuts import get_object_or_404


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
    Список исследователей, отсортированных по ФИО.
    В конце списка будут присутствовать "архивные" пользователи.
    """
    serializer_class = serializers.CustomUserSerializer
    pagination_class = StandardResultsSetPagination

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

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

        except Note.DoesNotExist:
            raise Http404


class UserDetail(generics.RetrieveAPIView):
    """
    Текущий пользователь
    """
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_object(self):
        return User.objects.get(username=self.request.user.get_username())


class NoteDetail(generics.GenericAPIView,
                 mixins.RetrieveModelMixin,
                 # mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin):
    serializer_class = serializers.NoteWithAuthorInfoSerializer
    lookup_url_kwarg = 'note_id'
    lookup_field = 'note_id'

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

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
    #     # TODO: обновление заметки вроде не нужно, убери миксин
    #     return self.update(request, *args, **kwargs)

    @transaction.atomic
    def destroy_note_and_relations_and_update_graph_data(self, request, *args, **kwargs):
        note_id = int(self.kwargs.get(self.lookup_url_kwarg))

        nodes_notes_relations = NodesNotesRelation.objects.filter(note_id=note_id)
        serializer = serializers.NodesNotesRelationSerializer(nodes_notes_relations, many=True).data
        for i in serializer:
            Graph.objects.get(graph_id=i['graph_id']).delete_node_from_dot(i['node_id'])

        Note.objects.get(note_id=note_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        return self.destroy_note_and_relations_and_update_graph_data(request, *args, **kwargs)


class NoteList(generics.ListCreateAPIView):
    serializer_class = serializers.NoteWithAuthorIDAndNodeIDSerializer
    queryset = NodesNotesRelation.objects.prefetch_related('note_id__user_id').order_by('note_id__created_at')
    pagination_class = StandardResultsSetPagination

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        note_data = {
            'url': validated_data['note_id']['url'],
            'research_id_id': validated_data['note_id']['research_id_id'],
            'user_id_id': validated_data['note_id']['user_id_id'],
        }
        if 'note_type' in validated_data['note_id']:
            note_data['note_type'] = validated_data['note_id']['note_type']
        else:
            pass  # TODO: здесь должно доставаться из латеха
        new_note = Note.objects.create(**note_data)

        if 'graph_id_id' in validated_data:
            try:
                graph = Graph.objects.get(graph_id=validated_data['graph_id_id'])
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND, exception='graph with such graph_id not exists')

            if not graph.node_with_node_id_exists(str(validated_data['node_id'])):
                return Response(status=status.HTTP_404_NOT_FOUND,
                                exception='node with such node_id not exists in graph')

            notes_nodes_rel_data = NodesNotesRelation(
                graph_id_id=validated_data['graph_id_id'],
                node_id=validated_data['node_id'],
                note_id_id=new_note.note_id,
            )
            notes_nodes_rel_data.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GraphDetail(generics.GenericAPIView,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    lookup_url_kwarg = 'graph_id'
    lookup_field = 'graph_id'

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

    # GET DETAIL
    def retrieve_get_object(self):
        try:
            graph_id = int(self.kwargs.get(self.lookup_url_kwarg))

            graph = Graph.objects.get(graph_id=graph_id)
            nodes = NodesNotesRelation.objects.filter(graph_id=graph_id)

            return graph, nodes
        except Note.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        graph, notes = self.retrieve_get_object()

        graph = serializers.GraphSerializer(graph).data
        notes = serializers.NodesNotesRelationSerializer(notes, many=True).data
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

            if 'title' in nodes_metadata[id]:
                full_nodes_info[id]['title'] = nodes_metadata[id]['title']

            if 'subgraph' in nodes_metadata[id]:
                full_nodes_info[id]['is_subgraph'] = True
                full_nodes_info[id]['subgraph_graph_id'] = nodes_metadata[id]['subgraph']
            else:
                full_nodes_info[id]['is_subgraph'] = False
                full_nodes_info[id]['subgraph_graph_id'] = 0

            full_nodes_info[id]['notes_ids'] = map_node_id_to_notes_ids[id]

        graph['notes_without_graph'] = notes_id_without_graph
        graph['nodes_metadata'] = full_nodes_info
        graph['levels'] = json.loads(graph['levels'])

        return Response(graph)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # UPDATE
    def get_object(self):
        try:
            graph_id = int(self.kwargs.get(self.lookup_url_kwarg))

            graph = Graph.objects.get(graph_id=graph_id)
            return graph
        except Note.DoesNotExist:
            raise Http404

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            update_type = request.query_params['update_type']
        except Note.DoesNotExist:
            raise Http404

        graph = self.get_object()

        if update_type == 'update_name':
            serialized = serializers.GraphNameSerializer(graph, data=request.data, partial=partial)
            serialized.is_valid(raise_exception=True)

        elif update_type == 'update_levels':
            serialized = serializers.GraphLevelsSerializer(graph, data=request.data, partial=partial)
            serialized.is_valid(raise_exception=True)

            serialized.instance.rewrite_graph_schema(request.data['levels'])

        elif update_type == 'update_metadata':
            serialized = serializers.GraphMetadataSerializer(graph, data=request.data, partial=partial)
            serialized.is_valid(raise_exception=True)

            serialized.instance.rewrite_node_metadata(request.data['node_id'], request.data['node_metadata'])

        else:
            raise BadRequest

        super().perform_update(serialized)

        if getattr(graph, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            graph._prefetched_objects_cache = {}

        return Response(serialized.data)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # DELETE

    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateGraph(generics.CreateAPIView):
    serializer_class = serializers.GraphSerializer


class NodeDetail(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated] TODO: включи
    serializer_class = serializers.NoteWithAuthorInfoSerializer

    def get_queryset(self):
        try:
            graph_id = int(self.kwargs.get('graph_id'))
            node_id = self.kwargs.get('node_id')

            obj = NodesNotesRelation.objects.filter(graph_id=graph_id, node_id=node_id).prefetch_related(
                'note_id').order_by('note_id__created_at')
            return obj
        except Note.DoesNotExist:
            raise Http404


class ResearchDetail(generics.RetrieveAPIView,
                     generics.UpdateAPIView,
                     generics.DestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated] TODO: включи
    lookup_url_kwarg = 'rsrch_id'

    def get_permissions(self):  # надо добавить всюду: добавить доступ только для препода
        return [permission() for permission in self.permission_classes]

    def get_object(self):
        try:
            rsrch_id = self.kwargs.get(self.lookup_url_kwarg)

            if self.request.method == 'GET':
                research = Research.objects. \
                    get(pk=rsrch_id)
                graphs = Graph.objects. \
                    filter(rsrch_id=rsrch_id). \
                    order_by('title')
                notes_without_graph = Note.objects. \
                    filter(rsrch_id=rsrch_id, nodesnotesrelation__graph_id_id__isnull=True)

                return research, graphs, notes_without_graph

            elif self.request.method in ('DELETE', 'PATCH'):
                research = Research.objects. \
                    get(pk=rsrch_id)

                return research

            else:
                raise BadRequest()

        except Note.DoesNotExist:
            raise Http404

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            kwargs.setdefault('context', self.get_serializer_context())
            return serializers.ResearchSerializer, \
                serializers.GraphNameSerializer, \
                serializers.NoteWithoutGraphSerializer

        elif self.request.method == 'PATCH':
            serializer = serializers.ResearchUpdateSerializer
            kwargs.setdefault('context', self.get_serializer_context())
            return serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        research, graphs, notes_without_graph = self.get_object()

        r_serialize = serializers.ResearchSerializer(research)
        research = r_serialize.data

        g_serializer = serializers.GraphNameSerializer(graphs, many=True)
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
        return super().destroy(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ResearchList(generics.CreateAPIView,
                   generics.ListAPIView):
    pagination_class = StandardResultsSetPagination

    # permission_classes = [permissions.IsAuthenticated] TODO: включи

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            serializer = serializers.ResearchSerializer
        elif self.request.method == 'POST':
            serializer = serializers.ResearchCreateSerializer

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

        except Note.DoesNotExist:
            raise Http404
