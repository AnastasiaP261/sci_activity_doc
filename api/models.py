from django.db import models
from django.contrib.auth.models import AbstractUser
from sci_activity_doc.settings import AUTH_USER_MODEL as user_model
import typing


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
    study_group = models.CharField("study_group", max_length=10, blank=True)

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

    def get_study_group(self) -> str:
        """
        Возвращает группу, в которой обучается студент
        """
        return self.study_group

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
        return self.title


class Graph(models.Model):
    """
    Граф TODO: дописать в соответствии с определением из курсача
    """

    graph_id = models.IntegerField(verbose_name="graph_id", primary_key=True)
    data = models.TextField(verbose_name="data")
    title = models.CharField(verbose_name="title", max_length=200, blank=False)

    research_id = models.ForeignKey(Research, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title


class Note(models.Model):
    """
    Заметка TODO: дописать в соответствии с определением из курсача
    """

    note_id = models.IntegerField(verbose_name="note_id", primary_key=True)
    url = models.URLField(verbose_name="url")  # по умолчанию max_length=200
    note_type = models.CharField(verbose_name="note_type", max_length=20)

    user_id = models.ForeignKey(user_model, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.note_type} {self.note_id}"
