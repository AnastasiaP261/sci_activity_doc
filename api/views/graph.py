import collections
import json

from django.core.exceptions import BadRequest
from django.db import transaction
from django.http import Http404
from rest_framework import generics, permissions
from rest_framework.response import Response

import api.serializers.graph
import api.serializers.note_and_node
from api import serializers
from api.views.consts import GET_METHOD, DELETE_METHOD, PATCH_METHOD
from auth_wrapper.license import IsOwnerObjectOrIsProfessorOrReadOnly
from core.models import Graph, NodesNotesRelation, Note


class GraphDetail(generics.RetrieveAPIView,
                  generics.UpdateAPIView,
                  generics.DestroyAPIView):
    lookup_url_kwarg = 'graph_id'
    lookup_field = 'graph_id'
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]

    def get_object(self):
        try:
            graph_id = int(self.kwargs.get(self.lookup_url_kwarg, 0))

            if self.request.method == GET_METHOD:
                graph = Graph.objects.get(graph_id=graph_id)
                nodes = NodesNotesRelation.objects.filter(graph_id=graph_id)

                self.check_object_permissions(self.request, graph)

                return graph, nodes

            if self.request.method in (DELETE_METHOD, PATCH_METHOD):
                graph = Graph.objects.get(graph_id=graph_id)

                self.check_object_permissions(self.request, graph)

                return graph

        except (Note.DoesNotExist, Graph.DoesNotExist, NodesNotesRelation.DoesNotExist):
            raise Http404()

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())

        if self.request.method == GET_METHOD:
            graph_serializer = api.serializers.graph.GraphSerializer
            nodes_notes_rel_serializer = api.serializers.note_and_node.NodesNotesRelationSerializer

            return graph_serializer(*args, **kwargs), nodes_notes_rel_serializer(*args, **kwargs)

        elif self.request.method == PATCH_METHOD:
            title_serializer = api.serializers.graph.GraphTitleUpdateSerializer
            metadata_serializer = api.serializers.graph.GraphMetadataUpdateSerializer
            levels_serializer = api.serializers.graph.GraphLevelsUpdateSerializer

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
    serializer_class = api.serializers.graph.GraphSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]
