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
            id=1,
            title='Листинг кода без определенного языка',
            description='ляляля',
            latex_reqex=r'\\begin{lstlisting}([\s\S]*?)\\end{lstlisting}',
            html_format_str='<listing style="font-family: Consolas,courier new;background-color: #f1f1f1;padding: 2px;font-size: 105%%;">\n%s\n</listing>',
            is_head=False,
        ).save()

        RemakeItem(
            title='Листинг кода с определенным языком',
            description='ляляля',
            latex_reqex=r'\\begin{lstlisting}\[.*\]([\s\S]*?)\\end{lstlisting}',
            html_format_str='<listing style="font-family: Consolas,courier new;background-color: #f1f1f1;padding: 2px;font-size: 105%%;">\n%s\n</listing>',
            is_head=True,
            child_item_id=1,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
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

    def test_format(self):
        text = r'''
            \textit{Чувствительность (или полнота)} -- это отношение извлеченных релевантных элементов ко всем релевантным элементам, доступным по теме. На практике его обычно представляют как процент релевантных статей по отношению к общему количеству уникальных релевантных статей при объединении всех результатов поиска.
            
            \section{\textbf{Метод}}
            Как правило, разработчики реализуют REST API с помощью протокола передачи гипертекста (HTTP). Метод HTTP сообщает серверу, что ему необходимо сделать с ресурсом. Ниже приведены четыре распространенных метода HTTP:
            
            \underline{GET.}
            Клиенты используют GET для доступа к ресурсам, расположенным на сервере по указанному URL. Они могут кэшировать~(определение~\ref{tab.rnd.edu.cash}) запросы GET и отправлять параметры в запросе REST API, чтобы сообщить серверу о необходимости фильтровать данные перед отправкой.

            \underline{\textbf{Заголовки HTTP}}}
            \emph{Заголовки запросов} — это некие дополнительные данные, которыми обмениваются клиент и сервер. Например, заголовок запроса указывает формат запроса и ответа, предоставляет информацию о статусе запроса и т. д.
        '''

        RemakeItem(
            title='Курсив textit',
            description='ляляля',
            latex_reqex=r'\\textit{(.*)}',
            html_format_str='<i>%s</i>',
            is_head=True,
        ).save()
        RemakeItem(
            title='Курсив emph',
            description='ляляля',
            latex_reqex=r'\\emph{(.*)}',
            html_format_str='<i>%s</i>',
            is_head=True,
        ).save()
        RemakeItem(
            title='Жирный шрифт',
            description='ляляля',
            latex_reqex=r'\\textbf{(.*)}',
            html_format_str='<b>%s</b>',
            is_head=True,
        ).save()
        RemakeItem(
            title='Подчеркивание',
            description='ляляля',
            latex_reqex=r'\\underline{(.*)}',
            html_format_str='<u>%s</u>',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''<i>
 Чувствительность (или полнота)
</i>
-- это отношение извлеченных релевантных элементов ко всем релевантным элементам, доступным по теме. На практике его обычно представляют как процент релевантных статей по отношению к общему количеству уникальных релевантных статей при объединении всех результатов поиска.
            
            \section{
<b>
 Метод}
</b>
Как правило, разработчики реализуют REST API с помощью протокола передачи гипертекста (HTTP). Метод HTTP сообщает серверу, что ему необходимо сделать с ресурсом. Ниже приведены четыре распространенных метода HTTP:
<u>
 GET.
</u>
Клиенты используют GET для доступа к ресурсам, расположенным на сервере по указанному URL. Они могут кэшировать~(определение~\\ref{tab.rnd.edu.cash}) запросы GET и отправлять параметры в запросе REST API, чтобы сообщить серверу о необходимости фильтровать данные перед отправкой.
<u>
 <b>
  Заголовки HTTP}
 </b>
</u>
<i>
 Заголовки запросов
</i>
— это некие дополнительные данные, которыми обмениваются клиент и сервер. Например, заголовок запроса указывает формат запроса и ответа, предоставляет информацию о статусе запроса и т. д.
''',
        )

    def test_headers(self):
        text = r'''
            \notestatement{rndcsedev}{Некоторые методологии разработки программного обеспечения (ПО)}
            \section{\textbf{Метод}}
            Как правило, разработчики реализуют REST API с помощью протокола передачи гипертекста (\gls{HTTP}). Метод \gls{HTTP} сообщает серверу, что ему необходимо сделать с ресурсом. Ниже приведены четыре распространенных метода \gls{HTTP}:
            
            \subsubsection{\textbf{Заголовки \gls{HTTP}}}
            Заголовки запросов — это некие дополнительные данные, которыми обмениваются клиент и сервер. Например, заголовок запроса указывает формат запроса и ответа, предоставляет информацию о статусе запроса и т. д.
            
            \subsection{Проведение вычислительных экспериментов}
        '''

        RemakeItem(
            title='Название заметки',
            description='ляляля',
            latex_reqex=r'\\notestatement{.*}{(.*)}',
            html_format_str='<h1>%s</h1>',
            is_head=True,
        ).save()
        RemakeItem(
            title='Заголовок первого уровня',
            description='ляляля',
            latex_reqex=r'\\section{(.*)}',
            html_format_str='<h2>%s</h2>',
            is_head=True,
        ).save()
        RemakeItem(
            title='Заголовок второго уровня',
            description='ляляля',
            latex_reqex=r'\\subsection{(.*)}',
            html_format_str='<h3>%s</h3>',
            is_head=True,
        ).save()
        RemakeItem(
            title='Заголовок третьего уровня',
            latex_reqex=r'\\subsubsection{(.*)}',
            html_format_str='<h4>%s</h4>',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''<h1>
 Некоторые методологии разработки программного обеспечения (ПО)
</h1>
<h2>
 \\textbf{Метод}
</h2>
Как правило, разработчики реализуют REST API с помощью протокола передачи гипертекста (\\gls{HTTP}). Метод \\gls{HTTP} сообщает серверу, что ему необходимо сделать с ресурсом. Ниже приведены четыре распространенных метода \\gls{HTTP}:
<h4>
 \\textbf{Заголовки \\gls{HTTP}}
</h4>
Заголовки запросов — это некие дополнительные данные, которыми обмениваются клиент и сервер. Например, заголовок запроса указывает формат запроса и ответа, предоставляет информацию о статусе запроса и т. д.
<h3>
 Проведение вычислительных экспериментов
</h3>
''',
        )

    def test_gls(self):
        text = r'''
            Для дальнейшего проектирования \gls{API} необходимо определить варианты использования (use-case) \gls{IS}.
            
            Как правило, разработчики реализуют REST API с помощью протокола передачи гипертекста (\gls{HTTP}). Метод \gls{HTTP} сообщает серверу, что ему необходимо сделать с ресурсом. Ниже приведены четыре распространенных метода \gls{HTTP}:

            Клиенты используют GET для доступа к ресурсам, расположенным на сервере по указанному \gls{URL}. Они могут кэшировать~(определение~\ref{tab.rnd.edu.cash}) запросы GET и отправлять параметры в запросе REST API, чтобы сообщить серверу о необходимости фильтровать данные перед отправкой.

            \subsubsection{\textbf{Заголовки \gls{HTTP}}}
        '''

        RemakeItem(
            title='Сокращение для API',
            description='ляляля',
            latex_reqex=r'\\gls{(API)}',
            html_format_str='%s',
            is_head=True,
        ).save()
        RemakeItem(
            title='Сокращение для HTTP',
            description='ляляля',
            latex_reqex=r'\\gls{(HTTP)}',
            html_format_str='%s',
            is_head=True,
        ).save()
        RemakeItem(
            title='Сокращение для IS',
            description='ляляля',
            latex_reqex=r'\\gls{IS}()',
            html_format_str='ИС%s',
            is_head=True,
        ).save()
        RemakeItem(
            title='Сокращение для URL',
            description='ляляля',
            latex_reqex=r'\\gls{(URL)}',
            html_format_str='%s',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''Для дальнейшего проектирования API необходимо определить варианты использования (use-case) ИС.
            
            Как правило, разработчики реализуют REST API с помощью протокола передачи гипертекста (HTTP). Метод HTTP сообщает серверу, что ему необходимо сделать с ресурсом. Ниже приведены четыре распространенных метода HTTP:

            Клиенты используют GET для доступа к ресурсам, расположенным на сервере по указанному URL. Они могут кэшировать~(определение~\\ref{tab.rnd.edu.cash}) запросы GET и отправлять параметры в запросе REST API, чтобы сообщить серверу о необходимости фильтровать данные перед отправкой.

            \subsubsection{\\textbf{Заголовки HTTP}}
''',
        )

    def test_line_wrapping(self):
        text = r'''
            Something in this document. This paragraph contains no information 
            and its purposes is to provide an example on how to insert white 
            spaces and lines breaks.\\
            When a line break is inserted, the text is not indented, there 
            are a couple of extra commands do line breaks. \newline
            This paragraph provides no information whatsoever. We are exploring 
            line breaks. \hfill \break
            And combining two commands
        '''

        RemakeItem(
            title='Перенос строки два слеша',
            description='ляляля',
            latex_reqex=r'\\\\()',
            html_format_str='<br>%s',
            is_head=True,
        ).save()
        RemakeItem(
            title='Перенос строки hfill и break',
            description='ляляля',
            latex_reqex=r'\\hfill \\break()',
            html_format_str='<br>%s',
            is_head=True,
        ).save()
        RemakeItem(
            title='Перенос строки newline',
            description='ляляля',
            latex_reqex=r'\\newline()',
            html_format_str='<br>%s',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''Something in this document. This paragraph contains no information 
            and its purposes is to provide an example on how to insert white 
            spaces and lines breaks.
<br/>
When a line break is inserted, the text is not indented, there 
            are a couple of extra commands do line breaks.
<br/>
This paragraph provides no information whatsoever. We are exploring 
            line breaks.
<br/>
And combining two commands
''',
        )

    def test_comments(self):
        text = r'''
            %----------------------------------------------------------
            
            % \subsubsection{Проведение вычислительных экспериментов}
            
            text text
            
            %-------
            %----------------------------------------------------------
            
            Для дальнейшего проектирования \gls{API} необходимо определить варианты использования (use-case) \gls{IS}.
            %--
            
            %----------------------------------------------------------
        '''

        RemakeItem(
            title='Обычный комментарий',
            description='ляляля',
            latex_reqex=r'^%[^-]()(.+)',
            html_format_str='%s',
            is_head=True,
        ).save()
        RemakeItem(
            title='Горизонтальная черта',
            description='ляляля',
            latex_reqex=r'^%()-{3,}',
            html_format_str='<hr>%s',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''%----------------------------------------------------------
            
            % \subsubsection{Проведение вычислительных экспериментов}
            
            text text
            
            %-------
            %----------------------------------------------------------
            
            Для дальнейшего проектирования \gls{API} необходимо определить варианты использования (use-case) \gls{IS}.
            %--
            
            %----------------------------------------------------------
''',
        )

    def test_just_text(self):
        text = r'''
            GET.
            Клиенты используют GET для доступа к ресурсам, расположенным на сервере по указанному URL. Они могут кэшировать запросы GET и отправлять параметры в запросе REST API, чтобы сообщить серверу о необходимости фильтровать данные перед отправкой.
            
            POST.
            Клиенты используют POST для отправки данных на сервер. При этом они включают в запрос представления данных. Отправка одного и того же запроса POST несколько раз имеет побочный эффект — многократное создание одного и того же ресурса.
            
            PUT.
            Клиенты используют PUT для обновления существующих на сервере ресурсов. В отличие от POST, отправка одного и того же запроса PUT несколько раз дает один и тот же результат в веб-службе REST (т.е. обладает идемпотентностью). 
            
            DELETE.
            Клиенты используют запрос DELETE для удаления ресурса. Запрос DELETE может изменить состояние сервера. Однако если у пользователя нет соответствующей аутентификации, запрос завершается ошибкой.
            '''

        RemakeItem(
            title='Какой-то тег',
            description='ляляля',
            latex_reqex=r'\\textit{(.*)}',
            html_format_str='<i>%s</i>',
            is_head=True,
        ).save()

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''GET.
            Клиенты используют GET для доступа к ресурсам, расположенным на сервере по указанному URL. Они могут кэшировать запросы GET и отправлять параметры в запросе REST API, чтобы сообщить серверу о необходимости фильтровать данные перед отправкой.
            
            POST.
            Клиенты используют POST для отправки данных на сервер. При этом они включают в запрос представления данных. Отправка одного и того же запроса POST несколько раз имеет побочный эффект — многократное создание одного и того же ресурса.
            
            PUT.
            Клиенты используют PUT для обновления существующих на сервере ресурсов. В отличие от POST, отправка одного и того же запроса PUT несколько раз дает один и тот же результат в веб-службе REST (т.е. обладает идемпотентностью). 
            
            DELETE.
            Клиенты используют запрос DELETE для удаления ресурса. Запрос DELETE может изменить состояние сервера. Однако если у пользователя нет соответствующей аутентификации, запрос завершается ошибкой.
''',
        )
