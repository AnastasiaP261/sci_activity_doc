from django.test import TestCase

from .models import RemakeItem


class TestRemakeItemManager_remake_latex_text(TestCase):
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
            latex_reqex=r'\\begin{itemize}\n+([\s\S]*?)\n+\\end{itemize}',
            html_format_str='<ul>\n%s\n</ul>',
            child_item_id=1,
            is_head=True,
        ).save()

        RemakeItem(
            title='Нумерованный список',
            description='ляляля',
            latex_reqex=r'\\begin{enumerate}\n+([\s\S]*?)\n+\\end{enumerate}',
            html_format_str='<ol>\n%s\n</ol>',
            child_item_id=1,
            is_head=True,
        ).save()

        res = RemakeItem.objects.all()
        for r in res:
            print(r)

        result = RemakeItem.objects.remake_latex_text(text)
        self.assertEqual(
            result,
            '''<ul>
<li>PsycINFO, платформа: OVIDSP;</li>
<li>Scopus;</li>
<li>SSA (Social Services Abstracts), платформа: Proquest;</li>
<li>SSCI (Social Sciences Citation Index), платформа: Web of Science.</li>
</ul>
lalalal
<ol>
<li>ASSIA (Applied Social Sciences Index and Abstracts), платформа: Proquest;</li>
<li>CINAHL Plus (Cumulative Index to Nursing and Allied Health Literature), платформа: EBSCOhost;</li>
<li>LISA (Library and Information Science Abstracts), платформа: Proquest;</li>
</ol>''',
        )


class TestRemakeItemManager__clean_text(TestCase):
    def test_1(self):
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

        result = RemakeItem.objects._clean_text(text)
        self.assertEqual(
            result,
            r'''\begin{itemize}
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
\end{enumerate}''',
        )

