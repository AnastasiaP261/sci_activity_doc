import json
import sys

from django.db import models
from sci_activity_doc.settings import AUTH_USER_MODEL as user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import re
import pydot
import collections
from django.core.exceptions import ValidationError, BadRequest, ObjectDoesNotExist


# Прим: ограничение max_length в типе models.TextField используется только тогда,
# когда поле отображается в формах (оно не применяется на уровне базы данных)

class User(AbstractUser):
    """
    Перегруженная модель пользователя позволяет добавить собственные настройки модели,
    в том числе новые поля и перегруженные методы
    """
    first_name = models.CharField("first_name", max_length=150, blank=False)
    surname = models.CharField("surname", max_length=150, blank=True)
    last_name = models.CharField("last_name", max_length=150, blank=False)
    study_group = models.CharField("study_group", max_length=15, blank=True)

    def get_full_name(self) -> str:
        """
        Возвращает фамилию + имя + отчество либо фамилия + имя, если отчество не заполнено.
        В качестве разделителя используется пробел
        """
        if self.surname:
            full_name = f"{self.last_name} {self.first_name} {self.surname}"

        else:
            full_name = f"{self.last_name} {self.first_name}"

        return full_name.strip()

    def get_short_full_name(self) -> str:
        """
        Возвращает ФИО в формате Фамилия И.О. либо Фамилия И. если отчество отсутствует
        """

        if self.surname:
            full_name = f"{self.last_name} {self.first_name[0]}. {self.surname[0]}."

        else:
            full_name = f"{self.last_name} {self.first_name[0]}."

        return full_name.strip()

    def get_groups_str(self) -> str:
        """
        Возвращает строку, в которой перечислены через запятую группы, в которых состоит пользователь
        :return:
        """
        return f'{", ".join([group.name for group in self.groups.all()])}'

    def get_groups_list(self) -> list:
        """
        Возвращает список, в которой перечислены через запятую группы, в которых состоит пользователь
        :return:
        """
        return [group.name for group in self.groups.all()]

    get_groups_str.short_description = u'groups'

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} {self.study_group}"


class Research(models.Model):
    """
    Исследование TODO: дописать в соответствии с определением из курсача
    """

    rsrch_id = models.CharField(verbose_name="rsrch_id", primary_key=True, max_length=30, blank=False)
    title = models.CharField(verbose_name="title", max_length=200, blank=False)
    description = models.TextField(verbose_name="description")
    start_date = models.DateField(verbose_name="start_date", help_text="Дата начала работы над исследованием")
    end_date = models.DateField(verbose_name="end_date",
                                help_text="Планируемая дата окончания работы над исследованием")
    created_at = models.DateTimeField(verbose_name='created_at', default=timezone.now)

    researchers = models.ManyToManyField(user_model, db_table="researches_users_relation")

    class Meta:
        permissions = (
            ("can_add_researchers_to", "Can add researchers to research"),
            ("can_add_graphs_to", "Can add graphs to research"),
        )

    def get_rsrchers_ids(self) -> str:
        """
         Возвращает строку, в которой перечислены id связанных исследователей
        """
        return f'{", ".join([str(user.id) for user in self.researchers.all()])}'

    def get_rsrchers_ids_list(self) -> list:
        """
         Возвращает список, в котором перечислены id связанных исследователей
        """
        return [user.id for user in self.researchers.all()]

    def get_researchers_names(self) -> str:
        """
        Возвращает строку, в которой перечислены Фамилия И.О. связанных исследователей
        :return:
        """
        return f'{", ".join([user.get_short_full_name() for user in self.researchers.all()])}'

    get_rsrchers_ids.short_description = u'rsrchers_ids'
    get_researchers_names.short_description = u'researchers_names'

    def __str__(self) -> str:
        return f'({self.rsrch_id}) {self.title.__str__()}'


DEFAULT_GRAPH = 'digraph{A;B;A->B;}'


class Graph(models.Model):
    """
    Граф TODO: дописать в соответствии с определением из курсача
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

    # МЕТОДЫ СВЯЗЕЙ

    def _get_edges_dict(self) -> dict:
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

    def _get_nodes_dict(self) -> dict:
        """
        Возвращает узлы в графе в формате словаря,
        где ключ - айди узла
        """
        nodes = self._get_dot().get_nodes()
        node_dict = {n.get_name(): n for n in nodes}

        return node_dict

    def _get_parents(self) -> dict:
        """
        Возвращает словарь, в котором для каждого индекса вершины графа указаны
        индексы родительских узлов
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

    def _get_children(self) -> dict:
        """
        Возвращает словарь, в котором для каждого индекса вершины графа указаны
        индексы дочерних узлов
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

    def _delete_node_from_dot(self, node_id: str):
        """
        Удаляет узел с переданным айди из графа и переподвязывает связанные с ним вершины
        """
        self._data_to_dot()
        dot = self._dot

        if node_id in ('A', 'B'):
            raise BadRequest()

        parents_dict = self._get_parents()
        parents_ids = list()
        if node_id in parents_dict:
            parents_ids = parents_dict[node_id]
        else:
            raise BadRequest()  # значит в графе нет узла с таким id

        children_dict = self._get_children()
        children_ids = list()
        if node_id in children_dict:
            children_ids = children_dict[node_id]

        dot.del_node(node_id)

        for i, edge in enumerate(dot.get_edges()):
            if node_id in edge.obj_dict['points']:
                dot.del_edge(edge.obj_dict['points'][0], edge.obj_dict['points'][1])

        for p in parents_ids:
            for ch in children_ids:
                dot.add_edge(pydot.Edge(src=p, dst=ch))

        self._dot = dot
        self._dot_to_data()

    def delete_node_from_dot(self, node_id: str):  # TODO: need tests, добавить проверку что нет
        self._delete_node_from_dot(node_id)
        self.save()

    def _rewrite_graph_schema(self, levels: dict) -> pydot.Dot:
        """
        Удаляет узел с переданным айди из графа
        """

        new_dot = pydot.graph_from_dot_data('digraph{}')[0]
        node_list = [i.get_name() for i in new_dot.get_nodes()]

        for _, nodes in levels.items():
            for node_id, prevs in nodes.items():
                if node_id not in node_list:
                    new_dot.add_node(pydot.Node(node_id))
                    node_list.append(node_id)
                for prev_node_id in prevs:
                    if prev_node_id not in node_list:
                        new_dot.add_node(pydot.Node(prev_node_id))
                        node_list.append(prev_node_id)
                    new_dot.add_edge(pydot.Edge(src=prev_node_id, dst=node_id))

        return new_dot

    def rewrite_graph_schema(self, levels: dict):
        new_dot = self._rewrite_graph_schema(levels)
        self.data = new_dot.to_string()
        self._data_to_dot()

    def _rewrite_node_metadata(self, node_id: str, new_matadata: dict) -> dict:
        old_metadata = self._get_nodes_dict()[node_id].obj_dict['attributes']

        def edit(key: str, new_val: str) -> dict:
            old_metadata[key] = new_val
            return old_metadata

        # если узел уже был подграфом и ему меняют айди
        if 'subgraph' in old_metadata and \
                new_matadata['is_subgraph'] == True and \
                new_matadata['subgraph_graph_id'] != old_metadata['subgraph']:

            return edit('subgraph', new_matadata['subgraph_graph_id'])

        # если узел не был подграфом и его делают подграфом
        elif 'subgraph' not in old_metadata and \
                new_matadata['is_subgraph'] == True:

            if len(new_matadata[
                       'notes_ids']) != 0:  # нельзя переопределить узел как подграф, пока к нему привязаны заметки
                raise BadRequest()

            return edit('subgraph', new_matadata['subgraph_graph_id'])

        elif 'title' not in old_metadata or \
                old_metadata['title'] != new_matadata['title']:

            return edit('title', new_matadata['title'].replace(' ', '_'))

        else:
            raise BadRequest()

    def rewrite_node_metadata(self, node_id: str, req_matadata: dict):
        new_matadata = self._rewrite_node_metadata(node_id, req_matadata)
        for i, node in enumerate(self._get_dot().get_nodes()):
            if node.get_name() == node_id:
                self._get_dot().get_nodes()[i].obj_dict['attributes'] = new_matadata

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
            attrs = node.obj_dict['attributes']
            if 'subgraph' in attrs:
                attrs['subgraph'] = int(attrs['subgraph'])
            metadata[node.obj_dict['name']] = attrs

        return metadata

    def get_nodes_metadata_json(self) -> str:
        return json.dumps(self._get_nodes_metadata_dict())

    def _dot_to_dict_levels(self) -> dict:
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


class Note(models.Model):
    """
    Заметка TODO: дописать в соответствии с определением из курсача
    """

    note_id = models.AutoField(verbose_name="note_id", primary_key=True)
    url = models.URLField(verbose_name="url", blank=False)  # по умолчанию max_length=200
    note_type = models.CharField(verbose_name="note_type", max_length=20)
    created_at = models.DateTimeField(verbose_name='created_at', default=timezone.now)

    rsrch_id = models.ForeignKey(Research, blank=False,  # тк заметка может быть не привязана к графу
                                 on_delete=models.CASCADE)
    user_id = models.ForeignKey(user_model, blank=False, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.note_id} {self.note_type}"


class NodesNotesRelation(models.Model):
    """
    Таблица связи для заметок и узлов.
    (узлы не будут описаны как модель, их node_id описаны в поле data в Графе)
    """

    id = models.AutoField(verbose_name="id", primary_key=True, help_text="просто идентификатор строки")
    # одна заметка может относиться к нескольким графам, к каждому единожды
    node_id = models.CharField(verbose_name="node_id", blank=False, max_length=3)

    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, blank=False)
    graph_id = models.ForeignKey(Graph, on_delete=models.CASCADE, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['note_id', 'graph_id'], name='unique note in graph'),
        ]
