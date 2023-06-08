from unittest import TestCase

from gitlab_client.parse_url import get_note_attributes


class Test_get_note_attributes(TestCase):
    def test_1(self):
        res = get_note_attributes(
            'https://some_host/rnd/rndcse/blob/master/rndcse_txb_Research/ResearchNotes/rndcse_not_dev_2021_11_21.tex')
        self.assertDictEqual(
            res,
            {
                'repo_id': 'rnd%2Frndcse',
                'branch_name': 'master',
                'file_path': 'rndcse_txb_Research%2FResearchNotes%2Frndcse_not_dev_2021_11_21.tex',
                'note_type': 'dev',
                'file_format': 'tex',
            },
        )

    def test_2(self):
        res = get_note_attributes(
            'https://sa2systems.ru:88/rnd/rndcse/blob/2021_rk6_71_petrichukao/readme.txt')
        self.assertDictEqual(
            res,
            {
                'repo_id': 'rnd%2Frndcse',
                'branch_name': '2021_rk6_71_petrichukao',
                'file_path': 'readme.txt',
                'note_type': '',
                'file_format': 'txt',
            },
        )
