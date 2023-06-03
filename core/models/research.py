from django.db import models
from django.utils import timezone

from sci_activity_doc.settings import AUTH_USER_MODEL as user_model


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
        verbose_name_plural = 'Researches'

    def get_rsrchers_ids(self) -> str:
        """
         Возвращает строку, в которой перечислены id связанных исследователей
        """
        return f'{", ".join([str(user.id) for user in self.researchers.all()])}'

    def get_user_ids(self) -> tuple:
        """
         Возвращает список, в котором перечислены id "владельцев".
         Этот метод необходим для определения прав доступа пользователя к объекту.
        """
        return tuple([user.id for user in self.researchers.all()])

    def get_researchers_names(self) -> str:
        """
        Возвращает строку, в которой перечислены Фамилия И.О. связанных исследователей
        :return:
        """
        return f'{", ".join([user.get_short_full_name() for user in self.researchers.all()])}'

    get_rsrchers_ids.short_description = u'researcher ids'
    get_researchers_names.short_description = u'researcher names'

    def __str__(self) -> str:
        return f'({self.rsrch_id}) {self.title.__str__()}'
