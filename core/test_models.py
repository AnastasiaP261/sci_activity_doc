import collections
from unittest import TestCase
from django.core.exceptions import ValidationError, BadRequest, ObjectDoesNotExist

import pydot

from .models import Graph


class TestGraph__dot_to_dict_levels(TestCase):
    def test_default_graph(self):
        graph = Graph(
            data='''
                 digraph { 
                     A; 
                     B; 
                     A -> B;
                 }
             ''',
        )
        self.assertEqual(
            graph._dot_to_dict_levels(),
            {
                0: {"A": []},
                1: {"B": ["A"]}
            },
            msg='начальный граф',
        )

    def test_graph_with_parallel_branches(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    B; 
                    A -> 1;
                    1 -> 2; 
                    2 -> 3; 
                    2 -> 4; 
                    2 -> 5; 
                    3 -> B; 
                    4 -> B; 
                    5 -> B; 
                }
                ''',
        )
        self.assertEqual(
            graph._dot_to_dict_levels(),
            {
                0: {"A": []},
                1: {"1": ["A"]},
                2: {'2': ['1']},
                3: {'3': ['2'], '4': ['2'], '5': ['2'], },
                4: {'B': ['3', '4', '5']},
            },
            msg='граф с распаралелливающимися ветками, сходящимися в один узел',
        )

    def test_graph_with_cross_level_edge(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    B; 
                    A -> B;
                    A -> 1; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> 4; 
                    4 -> B;
                }
            ''',
        )
        self.assertEqual(
            graph._dot_to_dict_levels(),
            {
                0: {"A": []},
                1: {"1": ["A"]},
                2: {'2': ['1']},
                3: {'3': ['2']},
                4: {'4': ['3']},
                5: {'B': ['4', 'A']},
            },
            msg='граф со связью, протягивающейся сквозь несколько уровней',
        )

    def test_graph_with_dead_end(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    B; 
                    A -> 1; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> 4; 
                    3 -> 5; 
                    5 -> B;
                }
            ''',
        )
        self.assertEqual(
            graph._dot_to_dict_levels(),
            {
                0: {"A": []},
                1: {"1": ["A"]},
                2: {'2': ['1']},
                3: {'3': ['2']},
                4: {'4': ['3'], '5': ['3']},
                5: {'B': ['5']},
            },
            msg='граф с тупиковой вершиной',
        )

    def test_graph_hard(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    6; 
                    7; 
                    8; 
                    9; 
                    10; 
                    B; 
                    A -> 1; 
                    1 -> 2;
                    1 -> 3; 
                    2 -> 4; 
                    2 -> 5; 
                    3 -> 6; 
                    3 -> 8; 
                    4 -> 7; 
                    5 -> 6; 
                    6 -> 7; 
                    6 -> 8; 
                    7 -> B; 
                    8 -> 9; 
                    9 -> 10;
                }
            ''',
        )
        self.assertEqual(
            graph._dot_to_dict_levels(),
            {
                0: {"A": []},
                1: {"1": ["A"]},
                2: {'2': ['1'], '3': ['1']},
                3: {'4': ['2'], '5': ['2']},
                4: {'6': ['3', '5']},
                5: {'7': ['4', '6'], '8': ['3', '6']},
                6: {'9': ['8']},
                7: {'10': ['9']},
                8: {'B': ['7']},
            },
            msg='сложный граф',
        )


class TestGraph__has_a_and_b_nodes(TestCase):
    def test_has_a_and_b_nodes(self):
        graph = Graph(
            data='''
                 digraph { 
                     A; 
                     1;
                     B; 
                     A -> 1;
                     1 -> B;
                 }
             ''',
        )
        self.assertTrue(
            graph._has_a_and_b_nodes(),
            msg='имеет A и B',
        )

    def test_hasnt_a_node(self):
        graph = Graph(
            data='''
                 digraph { 
                     1;
                     B; 
                     1 -> B;
                 }
             ''',
        )
        self.assertFalse(
            graph._has_a_and_b_nodes(),
            msg='нет вершины А',
        )

    def test_hasnt_b_node(self):
        graph = Graph(
            data='''
                     digraph { 
                         A; 
                         1;
                         A -> 1;
                     }
                 ''',
        )
        self.assertFalse(
            graph._has_a_and_b_nodes(),
            msg='нет вершины В',
        )


class TestGraph__has_duplicate_nodes(TestCase):
    def test_has_dupl_nodes(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    B; 
                    4;
                    A -> 1; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> 4; 
                    4 -> 5;
                    5 -> B;
                }
            ''',
        )
        self.assertTrue(
            graph._has_duplicate_nodes(),
            msg='дублируется node 4',
        )

    def test_hasnt_dupl_nodes(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    B; 
                    A -> 1; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> 4; 
                    4 -> 5;
                    5 -> B;
                }
            ''',
        )
        self.assertFalse(
            graph._has_duplicate_nodes(),
            msg='нет дублирующихся узлов',
        )


class TestGraph__has_cycle(TestCase):
    def test_has_cycle(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    B; 
                    A -> 1; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> 1; 
                    3 -> B;
                }
            ''',
        )
        self.assertTrue(
            graph._has_cycle(),
            msg='есть цикл',
        )

    def test_hasnt_cycle(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    B; 
                    A -> 1; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> B;
                }
            ''',
        )
        self.assertFalse(
            graph._has_cycle(),
            msg='нет цикла',
        )


class TestGraph__is_connected_graph(TestCase):
    def test_is_connected(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    B; 
                    A -> 1; 
                    1 -> B;
                }
            ''',
        )
        self.assertTrue(
            graph._is_connected_graph(),
            msg='все вершины графа связаны',
        )

    def test_isnt_connected1(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2;
                    3;
                    B; 
                    A -> 1; 
                    1 -> B;
                    2 -> 3;
                }
            ''',
        )
        self.assertFalse(
            graph._has_cycle(),
            msg='есть группа отдельных вершин',
        )

    def test_isnt_connected2(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    2;
                    B; 
                    A -> 1; 
                    1 -> B;
                }
            ''',
        )
        self.assertFalse(
            graph._has_cycle(),
            msg='есть единичная отдельная вершина',
        )


class TestGraph__all_nodes_exists(TestCase):
    def test_all_nodes_exists(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1; 
                    B; 
                    A -> 1; 
                    1 -> B;
                }
            ''',
        )
        self.assertTrue(
            graph._is_connected_graph(),
            msg='все вершины графа объявлены',
        )

    def test_with_not_exists_nodes(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    B; 
                    A -> 1; 
                    1 -> B;
                }
            ''',
        )
        self.assertFalse(
            graph._has_cycle(),
            msg='в связях участвует не объявленная вершина',
        )


class TestGraph__get_nodes_metadata(TestCase):
    def test_ok(self):
        graph = Graph(
            data='''
                digraph { 
                    A ; 
                    1 [subgraph=123, title=Cool_node]; 
                    2 ; 
                    3 []; 
                    B; 
                    A -> 1; 
                    1 -> 2; 
                    2 -> 3; 
                    3 -> B;
                }
            ''',
        )
        self.assertDictEqual(
            graph._get_nodes_metadata_dict(),
            {
                'A': {},
                '1': {'subgraph': 123, 'title': 'Cool_node'},
                '2': {},
                '3': {},
                'B': {},
            },
            msg='получение метаданных узлов',
        )


class TestGraph__rewrite_graph_schema(TestCase):
    def test_add_node_between(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    B; 
                    A -> B; 
                }
            ''',
        )
        new_levels = {
            '0': {"A": []},
            '1': {"1": ["A"]},
            '2': {"B": ["1"]},
        }

        self.assertEqual(
            graph._rewrite_graph_schema(new_levels).to_string(),
            '''digraph G {\nA;\n1;\nA -> 1;\nB;\n1 -> B;\n}\n''',
            msg='добавление узла между узлами'
        )

    def test_add_dead_end_node(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    B; 
                    A -> B; 
                }
            ''',
        )
        new_levels = {
            '0': {"A": []},
            '1': {"1": ["A"]},
            '2': {"B": ["A"]},
        }

        self.assertEqual(
            graph._rewrite_graph_schema(new_levels).to_string(),
            '''digraph G {\nA;\n1;\nA -> 1;\nB;\nA -> B;\n}\n''',
            msg='добавление тупикового узла',
        )


class TestGraph__rewrite_node_metadata(TestCase):
    def test_edit_subgraph_id(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1 [subgraph=123];
                    B; 
                    A -> 1; 
                    1 -> B; 
                }
            ''',
        )

        self.assertEqual(
            graph._rewrite_node_metadata('1', {'is_subgraph': True, 'subgraph_graph_id': 345,'notes_ids': []}),
            {'subgraph': 345},
            msg='изменение айди подграфа'
        )

    def test_set_subgraph_id_ok(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1;
                    B; 
                    A -> 1; 
                    1 -> B; 
                }
            ''',
        )

        self.assertEqual(
            graph._rewrite_node_metadata('1', {'is_subgraph': True, 'subgraph_graph_id': 123,'notes_ids': []}),
            {'subgraph': 123},
            msg='успешное изменение типа узла на "подграф"'
        )

    def test_set_subgraph_id_fail(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1;
                    B; 
                    A -> 1; 
                    1 -> B; 
                }
            ''',
        )

        with self.assertRaises(
                expected_exception=BadRequest,
                msg='нельзя изменить тип узла на "подграф", если к узлу привязаны заметки'):
            graph._rewrite_node_metadata('1', {'is_subgraph': True, 'subgraph_graph_id': 123, 'notes_ids': [1, 2]},)

    def test_edit_node_title(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1 [title=Old_title];
                    B; 
                    A -> 1; 
                    1 -> B; 
                }
            ''',
        )

        self.assertEqual(
            graph._rewrite_node_metadata('1', {'title': 'New title', 'is_subgraph': False}),
            {'title': 'New_title'},
            msg='изменение название узла'
        )

    def test_edit_node_title(self):
        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1;
                    B; 
                    A -> 1; 
                    1 -> B; 
                }
            ''',
        )

        self.assertEqual(
            graph._rewrite_node_metadata('1', {'title': 'New title', 'is_subgraph': False}),
            {'title': 'New_title'},
            msg='установка названия узла'
        )


class TestGraph__delete_node_from_dot(TestCase):
    """
    ↘ → ↗ - связи в графе
    ◯ - вершина графа
    ⊗ - удаляемая вершина графа
    ➤ - результирующий вид графа после удаления
    """

    def test_ok(self):
        """
        → ◯ → ⊗ → ◯    ➤   → ◯ → ◯
        """

        graph = Graph(
            data='''
                digraph { 
                    A; 
                    1;
                    B; 
                    A -> 1; 
                    1 -> B; 
                }
            ''',
        )

        graph._delete_node_from_dot("1")

        self.assertEqual(
            graph.data,
            'digraph G {\nA;\nB;\nA -> B;\n}\n',
            msg="удаление узла с одним ребенком и одним родителем"
        )
