from django.core.exceptions import BadRequest
from django.db import transaction
from django.http import Http404
from rest_framework import permissions, generics, filters
from rest_framework.response import Response

from api import serializers
from api.pagination import StandardResultsSetPagination
from api.views.consts import GET_METHOD, POST_METHOD, PATCH_METHOD, DELETE_METHOD
from auth_wrapper.license import IsOwnerObjectOrIsProfessorOrReadOnly, IsProfessorOrReadOnly
from core.models import Note, Graph, Research


class ResearchDetail(generics.RetrieveAPIView,
                     generics.UpdateAPIView,
                     generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]
    lookup_url_kwarg = 'rsrch_id'

    def get_permissions(self):
        def get_classes():
            if self.request.method == GET_METHOD:
                return [permissions.IsAuthenticated]

            elif self.request.method == DELETE_METHOD:
                return [permissions.IsAuthenticated, IsProfessorOrReadOnly]

            elif self.request.method == PATCH_METHOD:
                if 'researchers' in self.request.data:
                    return [permissions.IsAuthenticated, IsProfessorOrReadOnly]
                return [permissions.IsAuthenticated, IsOwnerObjectOrIsProfessorOrReadOnly]

        return [permission() for permission in get_classes()]

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

                self.check_object_permissions(self.request, research)

                return research, graphs, notes_without_graph

            elif self.request.method in (DELETE_METHOD, PATCH_METHOD):
                research = Research.objects. \
                    get(pk=rsrch_id)

                self.check_object_permissions(self.request, research)

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

        g_serializer = serializers.graph.GraphTitleUpdateSerializer(graphs, many=True)
        graphs = g_serializer.data

        n_serializer = serializers.note_and_node.NoteWithoutGraphInfoSerializer(notes_without_graph, many=True, required=False)
        notes_without_graph = n_serializer.data

        kwargs.setdefault('context', self.get_serializer_context())

        data = research
        data['graphs'] = graphs
        data['notes_without_graphs'] = notes_without_graph

        return Response(data)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        # по инструкциям CASCADE, здесь удалятся также записи всех связанных Graphs и NodesNotesRelations
        return super().destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ResearchList(generics.CreateAPIView,
                   generics.ListAPIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, IsProfessorOrReadOnly]
    filter_backends = [filters.SearchFilter, ]


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
