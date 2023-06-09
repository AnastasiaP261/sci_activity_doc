from django.db import models
from re import search, findall, DOTALL, sub


class RemakeItemManager(models.Manager):

    def _clean_text(self, text: str) -> str:
        lines = text.split('\n')
        dry_lines = list()
        for i, line in enumerate(lines):
            l = line.strip()
            if l == '':
                continue
            else:
                dry_lines.append(l)
        return '\n'.join(dry_lines)

    def remake_latex_text(self, text: str) -> str:
        items = self.filter(is_head=True)
        text = self._clean_text(text)

        for item in items:
            text = item.remake_latex_text(text)

        return text


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
                                            'например, у тега itemize, но не у тега item')

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
