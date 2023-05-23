import json
import sys

from django.db import models
from sci_activity_doc.settings import AUTH_USER_MODEL as user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import re
import pydot


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

    researchers = models.ManyToManyField(user_model, db_table="researches_users_relation")

    class Meta:
        permissions = (
            ("can_add_researchers_to", "Can add researchers to research"),
            ("can_add_graphs_to", "Can add graphs to research"),
        )

    def get_researchers_ids(self) -> str:
        """
         Возвращает строку, в которой перечислены id связанных исследователей
        """
        return f'{", ".join([str(user.id) for user in self.researchers.all()])}'

    def get_researchers_names(self) -> str:
        """
        Возвращает строку, в которой перечислены Фамилия И.О. связанных исследователей
        :return:
        """
        return f'{", ".join([user.get_short_full_name() for user in self.researchers.all()])}'

    get_researchers_ids.short_description = u'researchers_ids'
    get_researchers_names.short_description = u'researchers_names'

    def __str__(self) -> str:
        return f'({self.rsrch_id}) {self.title.__str__()}'


class Graph(models.Model):
    """
    Граф TODO: дописать в соответствии с определением из курсача
    """

    graph_id = models.AutoField(verbose_name="graph_id", primary_key=True)
    data = models.TextField(verbose_name="data", blank=True)
    title = models.CharField(verbose_name="title", max_length=200, blank=False)

    research_id = models.ForeignKey(Research, on_delete=models.CASCADE, blank=False)

    _dot = pydot.Dot

    def _data_to_dot(self):
        self._dot = pydot.graph_from_dot_data(self.data.__str__())[0]

    def _dot_to_data(self):
        self.data = self._dot.to_string()

    def delete_node_from_dot(self, node_id: int):
        self._data_to_dot()
        self._dot.del_node(node_id)
        self._dot_to_data()
        super().save()

    def node_with_node_id_exists(self, node_id: int) -> bool:
        self._data_to_dot()
        node_list = [i.get_name() for i in self._dot.get_nodes()]
        return str(node_id) in node_list

    def dot_to_json_elements(self) -> str:
        self._data_to_dot()
        edges = self._dot.get_edges()

        prev = dict()
        prev['A'] = set()
        for e in edges:
            i = e.obj_dict['points'][1]
            if i not in prev:
                prev[i] = set()
            prev[i].add(e.obj_dict['points'][0])
        for i in prev:
            prev[i] = sorted(list(prev[i]))

        levels = dict()

        def foo(i: str, lvl_count: int):
            if lvl_count not in levels:
                levels[lvl_count] = dict()
            for j in prev[i]:
                if i not in levels[lvl_count]:
                    levels[lvl_count][i] = set()
                levels[lvl_count][i].add(j)
                if j != 'A':
                    foo(j, lvl_count + 1)

        foo('B', 0)
        levels[len(levels)] = {'A': set()}
        for i in range(len(levels) // 2):
            levels[len(levels) - 1 - i], levels[i] = levels[i], levels[len(levels) - 1 - i]
        for i in levels:
            for j in levels[i]:
                levels[i][j] = sorted(list(levels[i][j]))

        return json.dumps(levels)

        class Meta:
            permissions = (
                ("can_edit_nodes", "Can edit graph nodes"),
                ("can_add_notes_to", "Can add notes to graph node"),
            )

        def __str__(self) -> str:
            return f'({self.graph_id.__str__()}) {self.title.__str__()}'


class Note(models.Model):
    """
    Заметка TODO: дописать в соответствии с определением из курсача
    """

    note_id = models.AutoField(verbose_name="note_id", primary_key=True)
    url = models.URLField(verbose_name="url", blank=False)  # по умолчанию max_length=200
    note_type = models.CharField(verbose_name="note_type", max_length=20)
    created_at = models.DateTimeField(verbose_name='created_at', default=timezone.now)

    research_id = models.ForeignKey(Research, blank=False,  # тк заметка может быть не привязана к графу
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

    note_id = models.ForeignKey(Note, on_delete=models.PROTECT, blank=False)
    graph_id = models.ForeignKey(Graph, on_delete=models.CASCADE, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['note_id', 'graph_id'], name='unique note in graph'),
        ]
