from django.db import models
from django.utils import timezone

from core.models.research import Research
from sci_activity_doc.settings import AUTH_USER_MODEL as user_model


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

    def get_user_ids(self) -> tuple:
        """
         Возвращает список, в котором перечислены id "владельцев".
         Этот метод необходим для определения прав доступа пользователя к объекту.
        """
        return tuple([user for user in [*self.rsrch_id.get_user_ids(), self.user_id_id]])
    rsrch_id.short_description=u'research'
    user_id.short_description=u'user'

    def __str__(self) -> str:
        return f"{self.note_id} {self.note_type}"
