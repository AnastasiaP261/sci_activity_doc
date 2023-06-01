from django.contrib.auth.models import AbstractUser
from django.db import models

# Прим: ограничение max_length в типе models.TextField используется только тогда,
# когда поле отображается в формах и сериализаторах (оно не применяется на уровне базы данных)

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
