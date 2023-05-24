from unittest import TestCase
from .models import Graph


class TestGraph(TestCase):
    def setUp(self):
        print("\nRunning setUp method...")

        self.def_graph = Graph(
            graph_id=1,
            data='''
                digraph { 
                    A; 
                    B; 
                    A -> B;
                }
            ''',
            title='GR_1',
        )
        self.graph_with_subgraphs = Graph(
            graph_id=2,
            data='''
                digraph { 
                    A; 
                    1 [subgraph=3]; 
                    2 [subgraph=4]; 
                    3 [subgraph=5]; 
                    4 [subgraph=6]; 
                    5 [subgraph=7]; 
                    B; 
                    A -> 2; 
                    2 -> 3; 
                    2 -> 4; 
                    2 -> 5; 
                    3 -> 1; 
                    4 -> 1; 
                    5 -> 1; 
                    1 -> B; 
                }
            ''',
            title='GR_2',
        )
        self.graph_with_cross_level_edge = Graph(
            graph_id=3,
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
                    A -> B;
                }
            ''',
            title='GR_3',
        )
        self.graph_without_a = Graph(
            graph_id=4,
            data='''
                digraph { 
                    1; 
                    2; 
                    3; 
                    4; 
                    5; 
                    B; 
                    1 -> 2;
                    2 -> 3; 
                    3 -> 4; 
                    4 -> 5; 
                    5 -> B;
                }
            ''',
            title='GR_4',
        )
        self.graph_without_b = Graph(
            graph_id=5,
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    A -> 1; 
                    1 -> 2;
                }
            ''',
            title='GR_5',
        )
        self.graph_with_cycle = Graph(
            graph_id=6,
            data='''
                digraph { 
                    A; 
                    1; 
                    2; 
                    B;
                    A -> 1; 
                    1 -> 2;
                    2 -> 1;
                    2 -> B;
                }
            ''',
            title='GR_6',
        )
        self.graph_with_dead_end = Graph(  # c тупиковым узлом (4)
            graph_id=7,
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
            title='GR_7',
        )
        self.graph_with_dupl_nodes = Graph(
            graph_id=8,
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
            title='GR_8',
        )

    def test_dot_to_json(self):
        self.assertEqual(self.def_graph.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"B": ["A"]}}')
        self.assertEqual(self.graph_with_subgraphs.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"2": ["A"]}, "2": {"3": ["2"], "4": ["2"], "5": ["2"]}, "3": {"1": ["3", "4", "5"]}, "4": {"B": ["1"]}}')
        self.assertEqual(self.graph_with_cross_level_edge.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"1": ["A"]}, "2": {"2": ["1"]}, "3": {"3": ["2"]}, "4": {"4": ["3"]}, "5": {"5": ["4"]}, "6": {"B": ["5", "A"]}}')
        self.assertEqual(self.graph_with_dead_end.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"1": ["A"]}, "2": {"2": ["1"]}, "3": {"3": ["2"]}, "4": {"4": ["3"], "5": ["3"]}, "5": {"B": ["5"]}}')
        self.assertEqual(self.graph_with_dupl_nodes.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"1": ["A"]}, "2": {"2": ["1"]}, "3": {"3": ["2"]}, "4": {"4": ["3"], "5": ["3"]}, "5": {"B": ["5"]}}')


    def test__has_a_and_b_nodes(self):
        self.assertTrue(self.def_graph._has_a_and_b_nodes())
        self.assertTrue(self.graph_with_subgraphs._has_a_and_b_nodes())
        self.assertTrue(self.graph_with_cross_level_edge._has_a_and_b_nodes())
        self.assertTrue(self.graph_with_dead_end._has_a_and_b_nodes())

        self.assertFalse(self.graph_without_a._has_a_and_b_nodes())
        self.assertFalse(self.graph_without_b._has_a_and_b_nodes())

    def test__has_duplicate_nodes(self):
        self.assertFalse(self.def_graph._has_duplicate_nodes())
        self.assertFalse(self.graph_with_subgraphs._has_duplicate_nodes())
        self.assertFalse(self.graph_with_cross_level_edge._has_duplicate_nodes())
        self.assertFalse(self.graph_with_dead_end._has_duplicate_nodes())

        self.assertTrue(self.graph_with_dupl_nodes._has_duplicate_nodes())


