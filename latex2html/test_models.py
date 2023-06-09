from django.test import TestCase

from .models import RemakeItem


class TestRemakeItemManager_remake_latex_text(TestCase):
    maxDiff = None

    def test_lists(self):
        text = r'''
            \begin{itemize}
                \item PsycINFO, платформа: OVIDSP;
                \item Scopus;
                
                \item SSA (Social Services Abstracts), платформа: Proquest;
                \item SSCI (Social Sciences Citation Index), платформа: Web of Science.
            \end{itemize}
            
            lalalal
            
            \begin{enumerate}
                \item ASSIA (Applied Social Sciences Index and Abstracts), платформа: Proquest;
                \item CINAHL Plus (Cumulative Index to Nursing and Allied Health Literature), платформа: EBSCOhost;
                \item LISA (Library and Information Science Abstracts), платформа: Proquest;
            \end{enumerate}
        '''

        RemakeItem(
            id=1,
            title='Элемент списка',
            description='ляляля',
            latex_reqex=r'\\item\s*(.*)',
            html_format_str='<li>%s</li>',
            is_head=False,
        ).save()

        RemakeItem(
            title='Не нумерованный список',
            description='ляляля',
            latex_reqex=r'\\begin{itemize}([\s\S]*?)\\end{itemize}',
            html_format_str='<ul>%s</ul>',
            child_item_id=1,
            is_head=True,
        ).save()

        RemakeItem(
            title='Нумерованный список',
            description='ляляля',
            latex_reqex=r'\\begin{enumerate}([\s\S]*?)\\end{enumerate}',
            html_format_str='<ol>%s</ol>',
            child_item_id=1,
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        print(result)
        self.assertEqual(
            result,
            '''<ul>
 <li>
  PsycINFO, платформа: OVIDSP;
 </li>
 <li>
  Scopus;
 </li>
 <li>
  SSA (Social Services Abstracts), платформа: Proquest;
 </li>
 <li>
  SSCI (Social Sciences Citation Index), платформа: Web of Science.
 </li>
</ul>
lalalal
<ol>
 <li>
  ASSIA (Applied Social Sciences Index and Abstracts), платформа: Proquest;
 </li>
 <li>
  CINAHL Plus (Cumulative Index to Nursing and Allied Health Literature), платформа: EBSCOhost;
 </li>
 <li>
  LISA (Library and Information Science Abstracts), платформа: Proquest;
 </li>
</ol>
''',
        )

    def test_listing(self):
        text = r'''
            Класс графа содержит такие поля как:

            \begin{lstlisting}[language=Python]
            class Graph(models.Model):
                graph_id = models.IntegerField(verbose_name="graph_id", primary_key=True)
                data = models.TextField(verbose_name="data")
                title = models.CharField(verbose_name="title", max_length=200, blank=False)
            
                research_id = models.ForeignKey(Research, on_delete=models.CASCADE)
            \end{lstlisting}
            
            Класс заметки содержит поля:
            
            \begin{lstlisting}
            class Note(models.Model):
                note_id = models.IntegerField(verbose_name="note_id", primary_key=True)
                url = models.URLField(verbose_name="url")  # по умолчанию max_length=200
                note_type = models.CharField(verbose_name="note_type", max_length=20)
            
                user_id = models.ForeignKey(user_model, on_delete=models.PROTECT)
            \end{lstlisting}
            '''

        RemakeItem(
            title='Листинг кода с определенным языком',
            description='ляляля',
            latex_reqex=r'\\begin{lstlisting}\[.*\]([\s\S]*?)\\end{lstlisting}',
            html_format_str='<listing style="font-family: Consolas,courier new;background-color: #f1f1f1;padding: 2px;font-size: 105%%;">\n%s\n</listing>',
            is_head=True,
        ).save()

        RemakeItem(
            title='Листинг кода без определенного языка',
            description='ляляля',
            latex_reqex=r'\\begin{lstlisting}([\s\S]*?)\\end{lstlisting}',
            html_format_str='<listing style="font-family: Consolas,courier new;background-color: #f1f1f1;padding: 2px;font-size: 105%%;">\n%s\n</listing>',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        print(result)
        self.assertEqual(
            result,
            '''Класс графа содержит такие поля как:
<listing style="font-family: Consolas,courier new;background-color: #f1f1f1;padding: 2px;font-size: 105%;">
 class Graph(models.Model):
                graph_id = models.IntegerField(verbose_name="graph_id", primary_key=True)
                data = models.TextField(verbose_name="data")
                title = models.CharField(verbose_name="title", max_length=200, blank=False)
            
                research_id = models.ForeignKey(Research, on_delete=models.CASCADE)
</listing>
Класс заметки содержит поля:
<listing style="font-family: Consolas,courier new;background-color: #f1f1f1;padding: 2px;font-size: 105%;">
 class Note(models.Model):
                note_id = models.IntegerField(verbose_name="note_id", primary_key=True)
                url = models.URLField(verbose_name="url")  # по умолчанию max_length=200
                note_type = models.CharField(verbose_name="note_type", max_length=20)
            
                user_id = models.ForeignKey(user_model, on_delete=models.PROTECT)
</listing>
''',
            )
