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

    def test_dot_to_json(self):
        self.assertEqual(self.def_graph.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"B": ["A"]}}')
        self.assertEqual(self.graph_with_subgraphs.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"2": ["A"]}, "2": {"3": ["2"], "4": ["2"], "5": ["2"]}, "3": {"1": ["3", "4", "5"]}, "4": {"B": ["1"]}}')
        self.assertEqual(self.graph_with_cross_level_edge.dot_to_json_elements(),
                         r'{"0": {"A": []}, "1": {"1": ["A"]}, "2": {"2": ["1"]}, "3": {"3": ["2"]}, "4": {"4": ["3"]}, "5": {"5": ["4"]}, "6": {"B": ["5", "A"]}}')
