from django.db import models
from re import search, findall, DOTALL, sub
from bs4 import BeautifulSoup as bs


class RemakeItemManager(models.Manager):

    def remake_latex_text(self, text: str) -> str:
        items = self.filter(is_head=True)

        for item in items:
            text = item.remake_latex_text(text)

        soup = bs(text)
        pretty_html = soup.prettify()

        return pretty_html


class RemakeItem(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, unique=True,
                             help_text='Краткое название - что переделывает этот RemakeItem')

    description = models.TextField(blank=False, null=False,
                                   help_text='Подробное описание того, что этот тег должен делать.' \
                                             'Описание желательно составлять так, чтобы другой человек мог понять как ' \
                                             'это работает и свою ошибку, если она есть и исправить ее')

    latex_reqex = models.TextField(blank=False, null=False,
                                   help_text='Регулярное выражение, вычленяющее содержимое тэга/команды')

    html_format_str = models.TextField(blank=True, null=False,
                                       help_text='Текст, содержащий шаблоны и операторы форматирорования строк ' \
                                                 '(в них вставится текст, вытащенный из latex_reqex)')

    child_item = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                                   help_text='Заполняется, если тег имеет подтеги')

    is_head = models.BooleanField(null=False, blank=False,
                                  help_text='Это значение равно True только у самостоятельных тегов, ' \
                                            'например, у тега itemize, но не у тега item. Также, с помощью этого ' \
                                            'значения можно выставить порядок выполнения преобразований.')

    objects = RemakeItemManager()

    def remake_latex_text(self, text: str) -> str:
        while True:
            match = search(self.latex_reqex, text)
            if match:
                extracted = match.group(1)
                new_text_part = self.html_format_str % extracted
                if self.child_item_id:
                    new_text_part = self.child_item.remake_latex_text(new_text_part)
                text = text.replace(match.group(), new_text_part, 1)
            else:
                return text
