from django.db import models

from core.models.graph import Graph
from core.models.note import Note


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

    def get_user_ids(self) -> tuple:
        """
         Возвращает список, в котором перечислены id "владельцев".
         Этот метод необходим для определения прав доступа пользователя к объекту.
        """
        return tuple([user for user in self.graph_id.get_user_ids()])
