import collections
import json
import re
from typing import Dict, List, Tuple, Set

import pydot
from django.core.exceptions import ValidationError, BadRequest
from django.db import models

from core.models.research import Research

DEFAULT_GRAPH = 'digraph{A;B;A->B;}'


class Graph(models.Model):
    """
    Граф - совокупность множества узлов (вершин, nodes), связанных между собой.
    Отражает ход работы над исследованием.
    """

    graph_id = models.AutoField(verbose_name="graph_id", primary_key=True)
    data = models.TextField(verbose_name="data", blank=False, default=DEFAULT_GRAPH)
    title = models.CharField(verbose_name="title", max_length=200, blank=False)

    rsrch_id = models.ForeignKey(Research, on_delete=models.CASCADE, blank=False)

    _dot = pydot.Dot  # обращаться только через геттер _get_dot! Это гарантирует актуальность данных

    class Meta:
        permissions = (
            ("can_edit_nodes", "Can edit graph nodes"),
            ("can_add_notes_to", "Can add notes to graph node"),
        )

    rsrch_id.short_description = u'researchers'
    data.short_description = u'DOT-data'

    def get_user_ids(self) -> Tuple[int]:
        """
         Возвращает список, в котором перечислены id "владельцев".
         Этот метод необходим для определения прав доступа пользователя к объекту.
        """
        return tuple([int(user) for user in self.rsrch_id.get_user_ids()])

    # ПЕРЕОПРЕДЕЛЕННЫЕ МЕТОДЫ

    def delete(self, using=None, keep_parents=False):
        return super().delete(using, keep_parents)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        Переопределение метода safe
        """
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        """
        Переопределение метода full_clean
        """
        self._clean_data()
        if self.valid_graph():
            super().full_clean(exclude, validate_unique, validate_constraints)
        else:
            raise ValidationError()

    def _clean_data(self):
        """
        Очищает входящий текст от лишних пробельных символов
        """
        self.data = re.sub(r'\s', '', self.data.__str__())

    def __str__(self) -> str:
        return f'({self.graph_id.__str__()}) {self.title.__str__()}'

    # МЕТОДЫ DOT

    def _data_to_dot(self):
        """
        Записывает очищенный текст в переменную класса в формате pydot
        """
        self._clean_data()
        self._dot = pydot.graph_from_dot_data(self.data)[0]

    def _dot_to_data(self):
        """
        Записывает данные из dot в текстовый формат
        """
        self.data = self._dot.to_string()

    def _get_dot(self) -> pydot.Dot:
        """
        Геттер для данных в формате dot
        """
        self._data_to_dot()
        return self._dot

    def _get_node_metadata(self, node_id: str) -> Dict[str, any]:
        return self._get_nodes_dict()[node_id][0]['attributes']

    # МЕТОДЫ СВЯЗЕЙ

    def _get_edges_dict(self) -> Dict[str, List[pydot.Edge]]:
        """
        Возвращает связи в графе в формате словаря,
        где ключ - айди узла, из которого идет грань
        """
        edges = self._get_dot().get_edges()

        dict_edges = dict()
        for e in edges:
            if e.obj_dict['points'][0] not in dict_edges:
                dict_edges[e.obj_dict['points'][0]] = list()
            dict_edges[e.obj_dict['points'][0]].append(e.obj_dict)

        return dict_edges

    # МЕТОДЫ УЗЛОВ

    def _get_nodes_dict(self) -> Dict[str, pydot.Node]:
        """
        Возвращает узлы в графе в формате словаря,
        где ключ - айди узла.

        Не предназначен для мутации!
        """

        return self._get_dot().obj_dict['nodes']

    def _get_parents(self) -> Dict[str, Set[pydot.Node]]:
        """
        Возвращает словарь, в котором для каждого индекса вершины графа указаны
        индексы родительских узлов.

        Не предназначен для мутации!
        """
        prev = dict()

        prev['A'] = set()
        for e in self._get_dot().get_edges():
            i = e.obj_dict['points'][1]
            if i not in prev:
                prev[i] = set()
            prev[i].add(e.obj_dict['points'][0])
        for i in prev:
            prev[i] = sorted(list(prev[i]))

        return prev

    def _get_children(self) -> Dict[str, Set[pydot.Node]]:
        """
        Возвращает словарь, в котором для каждого индекса вершины графа указаны
        индексы дочерних узлов.

        Не предназначен для мутации!
        """
        next = dict()
        for e in self._get_dot().get_edges():
            i = e.obj_dict['points'][0]
            if i not in next:
                next[i] = set()
            next[i].add(e.obj_dict['points'][1])
            if e.obj_dict['points'][1] not in next:
                next[e.obj_dict['points'][1]] = set()

        return next

    def rewrite_graph_schema(self, levels: Dict[int, Dict[str, List[str]]]):
        """
        Переписывает схему графа в соответствии с новым переданным levels.

        Не вызывает метод save!
        """
        new_dot: pydot.Dot = pydot.graph_from_dot_data('digraph{}')[0]
        node_list = [i.get_name() for i in new_dot.get_nodes()]
        old_nodes = self._get_nodes_dict()

        for _, nodes in levels.items():
            for node_id, prevs in nodes.items():
                if node_id not in node_list:
                    old_attrs = dict()
                    if node_id in old_nodes:
                        old_attrs = self._get_node_metadata(node_id)
                    new_dot.add_node(pydot.Node(node_id, **old_attrs))
                    node_list.append(node_id)
                for prev_node_id in prevs:
                    if prev_node_id not in node_list:
                        new_dot.add_node(pydot.Node(prev_node_id))
                        node_list.append(prev_node_id)
                    new_dot.add_edge(pydot.Edge(src=prev_node_id, dst=node_id))

        self._dot = new_dot
        self._dot_to_data()

    def _rewrite_node_metadata(self, node_id: str, new_matadata: Dict[str, any]) -> Dict[str, any]:
        old_metadata = self._get_nodes_dict()[node_id][0]['attributes']

        def edit(key: str, new_val: str) -> dict:
            old_metadata[key] = new_val
            return old_metadata

        was_subgraph = int(old_metadata.get('subgraph', 0)) != 0
        make_subgraph = new_matadata['is_subgraph']
        change_id = make_subgraph and \
                    int(new_matadata.get('subgraph_graph_id', 0)) != int(old_metadata.get('subgraph', 0))

        # если узел уже был подграфом и ему меняют айди
        if was_subgraph and change_id:
            return edit('subgraph', new_matadata['subgraph_graph_id'])

        # если узел не был подграфом и его делают подграфом
        elif not was_subgraph and make_subgraph:
            # нельзя переопределить узел как подграф, пока к нему привязаны заметки
            if new_matadata['notes_ids']:
                raise BadRequest()

            return edit('subgraph', new_matadata['subgraph_graph_id'])

        # если узел был подграфом и его делают не подграфом
        elif was_subgraph and not make_subgraph:
            return edit('subgraph', '0')

        elif old_metadata.get('title', '') != new_matadata['title'].strip():
            return edit('title', new_matadata['title'].replace(' ', '_').strip())

        else:
            raise BadRequest()

    def rewrite_node_metadata(self, node_id: str, req_matadata: Dict[str, any]):
        self._data_to_dot()
        new_matadata = self._rewrite_node_metadata(node_id, req_matadata)
        self._dot.obj_dict['nodes'][node_id][0]['attributes'] = new_matadata
        self._dot_to_data()

    def node_with_node_id_exists(self, node_id: str) -> bool:  # TODO: need tests
        """
        Проверяет, что в графе существует узел с переданным айди
        """
        node_list = [i.get_name() for i in self._get_dot().get_nodes()]
        return str(node_id) in node_list

    def _get_nodes_metadata_dict(self) -> dict:
        nodes = self._get_dot().get_nodes()

        metadata = dict()
        for node in nodes:
            attrs = dict()
            attrs['subgraph'] = int(node.obj_dict['attributes'].get('subgraph', 0))
            attrs['title'] = node.obj_dict['attributes'].get('title', '').replace('_', ' ').replace('"', '')
            metadata[node.obj_dict['name']] = attrs

        return metadata

    def get_nodes_metadata_json(self) -> str:
        return json.dumps(self._get_nodes_metadata_dict())

    def _dot_to_dict_levels(self) -> Dict[int, Dict[str, List[str]]]:
        """
        Приводит к следующему виду:
        {
            <номер_уровня: int>: {
                <айди_узла: str>: [
                    <айди_родительского_узла: str>,
                     ...,
                ],
                ...,
            },
            ...,
        }

        Где уровень -- это глубина отдаления вершины от начальной(А).
        Например, граф

            A -> 1 -> 2 -> 4 -> B
                 └--> 3 __⤴

        будет разделен на уровни:

         |    |    |    |    |    |
            A -> 1 -> 2 -> 4 -> B
                 └--> 3 __⤴
         |    |    |    |    |    |
         | 0  | 1  | 2  | 3  | 5  |

        где узел А окажется на уровне 0, узел 1 на уровне 2,
        узлы 2 и 3 на уровне 2,
        а узлы 4 и B на уровнях 3 и 5 соответсвенно.
        """

        dict_edges = self._get_edges_dict()

        # обход в глубину, получаем уровни для всех вершин
        edges_levels = collections.defaultdict(int)

        def breadth_first_traversal(edge_index: str, level: int):
            edges_levels[edge_index] = max(level, edges_levels[edge_index])
            if edge_index not in dict_edges:
                return
            for next_edge in dict_edges[edge_index]:
                breadth_first_traversal(next_edge['points'][1], level + 1)

        # B всегда должна быть на последнем уровне
        breadth_first_traversal('A', 0)
        for edge, level in edges_levels.items():
            if edge == 'B':
                continue
            if level >= edges_levels['B']:
                edges_levels['B'] += 1

        # список родительских вершин для каждой вершины
        prev = self._get_parents()

        # формируем итоговую структуру
        raw_result = collections.defaultdict(dict)
        for edge_index, edge_level in edges_levels.items():
            raw_result[edge_level][edge_index] = prev[edge_index]

        return dict(raw_result)

    def dot_to_json_levels(self) -> str:
        return json.dumps(self._dot_to_dict_levels())

    # ВАЛИДАТОРЫ

    def valid_graph(self) -> bool:
        if not self._has_a_and_b_nodes():
            return False

        if self._has_cycle():
            return False

        if self._has_duplicate_nodes():
            return False

        if not self._is_connected_graph():
            return False

        if not self._all_nodes_exists():
            return False

        return True

    class CycleDetectedError(Exception):
        """
        Найден цикл
        """

        def __init__(self, graph_id: int):
            self.graph_id = graph_id
            self.message = f"Graph {self.graph_id} has cycle"
            super().__init__(self.message)

    def _has_a_and_b_nodes(self) -> bool:
        return self.node_with_node_id_exists('A') and self.node_with_node_id_exists('B')

    def _has_cycle(self) -> bool:
        # список дочерних вершин для каждой вершины
        next = self._get_children()

        # используем алгоритм обхода в глубину для поиска цикла
        # см https://neerc.ifmo.ru/wiki/index.php?title=%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BE%D0%B1%D1%85%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%B3%D0%BB%D1%83%D0%B1%D0%B8%D0%BD%D1%83_%D0%B4%D0%BB%D1%8F_%D0%BF%D0%BE%D0%B8%D1%81%D0%BA%D0%B0_%D1%86%D0%B8%D0%BA%D0%BB%D0%B0
        WHITE = 'w'
        GRAY = 'g'
        BLACK = 'b'
        color = {i: WHITE for i in next}

        def breadth_first_traversal(edge_index: str):
            color[edge_index] = GRAY

            for next_index in next[edge_index]:
                if color[next_index] == WHITE:
                    breadth_first_traversal(next_index)
                if color[next_index] == GRAY:
                    raise self.CycleDetectedError(graph_id=self.graph_id)

            color[edge_index] = BLACK

        try:
            breadth_first_traversal('A')
        except self.CycleDetectedError:
            return True

        return False

    def _has_duplicate_nodes(self) -> bool:
        nodes = self._get_dot().get_nodes()

        nodes_list = list()
        for n in nodes:
            nodes_list.append(n.obj_dict['name'])
        nodes_set = set(nodes_list)

        return len(nodes_set) != len(nodes_list)

    def _is_connected_graph(self) -> bool:
        # список дочерних вершин для каждой вершины
        next = self._get_children()

        set_of_nodes = set()

        def breadth_first_traversal(edge_index: str):
            set_of_nodes.add(edge_index)
            for next_index in next[edge_index]:
                breadth_first_traversal(next_index)

        breadth_first_traversal('A')

        return len(set_of_nodes) == len(next)

    def _all_nodes_exists(self) -> bool:
        # список дочерних вершин для каждой вершины
        next = self._get_children()

        set_of_nodes = set()

        def breadth_first_traversal(edge_index: str):
            set_of_nodes.add(edge_index)
            for next_index in next[edge_index]:
                breadth_first_traversal(next_index)

        breadth_first_traversal('A')

        return len(set_of_nodes) == len(next)
