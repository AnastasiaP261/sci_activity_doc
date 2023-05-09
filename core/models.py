from django.db import models
from sci_activity_doc.settings import AUTH_USER_MODEL as user_model


# Прим: ограничение max_length в типе models.TextField используется только тогда,
# когда поле отображается в формах (оно не применяется на уровне базы данных)

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
        return self.title.__str__()


class Graph(models.Model):
    """
    Граф TODO: дописать в соответствии с определением из курсача
    """

    graph_id = models.IntegerField(verbose_name="graph_id", primary_key=True)
    data = models.TextField(verbose_name="data")
    title = models.CharField(verbose_name="title", max_length=200, blank=False)

    research_id = models.ForeignKey(Research, on_delete=models.CASCADE, blank=False)

    class Meta:
        permissions = (
            ("can_edit_nodes", "Can edit graph nodes"),
            ("can_add_notes_to", "Can add notes to graph node"),
        )

    def __str__(self) -> str:
        return self.title.__str__()


class Note(models.Model):
    """
    Заметка TODO: дописать в соответствии с определением из курсача
    """

    note_id = models.IntegerField(verbose_name="note_id", primary_key=True)
    url = models.URLField(verbose_name="url", blank=False)  # по умолчанию max_length=200
    note_type = models.CharField(verbose_name="note_type", max_length=20)

    research_id = models.ForeignKey(Research, blank=False,
                                    on_delete=models.CASCADE)  # тк заметка может быть не привязана к графу
    user_id = models.ForeignKey(user_model, blank=False, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.note_type} {self.note_id}"


class NodesNotesRelation(models.Model):
    """
    Таблица связи для заметок и узлов.
    (узлы не будут описаны как модель, их node_id описаны в поле data в Графе)
    """

    id = models.IntegerField(verbose_name="id", primary_key=True, help_text="просто идентификатор строки")
    node_id = models.IntegerField(verbose_name="node_id", blank=False)

    note_id = models.ForeignKey(Note, on_delete=models.PROTECT, blank=False)
    graph_id = models.ForeignKey(Graph, on_delete=models.PROTECT, blank=False)
