from django.db import models
from django.contrib.auth.models import AbstractUser
from sci_activity_doc.settings import AUTH_USER_MODEL as user_model


# Прим: ограничение max_length в типе models.TextField используется только тогда,
# когда поле отображается в формах (оно не применяется на уровне базы данных)

class User(AbstractUser):
    """
    Перегруженная модель пользователя позволяет добавить собственные настройки модели,
    в том числе новые поля и перегруженные методы
    """
    first_name = models.CharField("first name", max_length=150, blank=False)
    surname = models.CharField("surname", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=False)
    study_group = models.CharField("study_group", max_length=10, blank=True)

    def get_full_name(self) -> str:
        """
        Возвращает фамилию + имя + отчество либо фамилия + имя, если отчество не заполнено.
        В качестве разделителя используется пробел
        """
        if self.surname:
            full_name = "%s %s %s" % (self.last_name, self.first_name, self.surname)
        else:
            full_name = "%s %s" % (self.last_name, self.first_name)

        return full_name.strip()

    def get_study_group(self) -> str:
        """
        Возвращает группу, в которой обучается студент
        """
        return self.study_group

    def __str__(self) -> str:
        return "%s %s %s" % (self.last_name, self.first_name, self.study_group)


class Research(models.Model):
    """
    Исследование TODO: дописать в соответствии с определением из курсача
    """

    id = models.CharField("rsrch_id", primary_key=True, max_length=30, blank=False)
    title = models.CharField("title", max_length=200, blank=False)
    description = models.TextField("description")
    start_date = models.DateField("start_date", help_text="Дата начала работы над исследованием")
    end_date = models.DateField("end_date", help_text="Планируемая дата окончания работы над исследованием")

    researchers = models.ManyToManyField(user_model, db_table="researches_users_relation")

