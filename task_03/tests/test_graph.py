import pytest

from task_03.graph import Graph


class TestGraphBasics:
    def test_empty_graph(self):
        g = Graph()
        assert len(g) == 0
        assert g.nodes == set()
        assert "A" not in g
        assert g.neighbors("A") == []

    def test_repr(self):
        assert "undirected" in repr(Graph(directed=False))
        assert "directed" in repr(Graph(directed=True))

    def test_default_is_undirected(self):
        assert Graph().directed is False


class TestUndirectedEdges:
    def test_single_edge_adds_both_directions(self):
        g = Graph()
        g.add_edge("A", "B", 5)
        assert ("B", 5) in g.neighbors("A")
        assert ("A", 5) in g.neighbors("B")
        assert g.nodes == {"A", "B"}
        assert len(g) == 2

    def test_multiple_edges(self):
        g = Graph()
        g.add_edge("A", "B", 1)
        g.add_edge("B", "C", 2)
        g.add_edge("A", "C", 3)
        assert g.nodes == {"A", "B", "C"}
        assert sorted(g.neighbors("A")) == sorted([("B", 1), ("C", 3)])

    def test_self_loop(self):
        g = Graph()
        g.add_edge("A", "A", 4)
        assert g.neighbors("A").count(("A", 4)) == 2  # undirected double-adds

    def test_parallel_edges_kept(self):
        g = Graph()
        g.add_edge("A", "B", 5)
        g.add_edge("A", "B", 3)
        assert g.neighbors("A").count(("B", 5)) == 1
        assert g.neighbors("A").count(("B", 3)) == 1


class TestDirectedEdges:
    def test_single_directed_edge(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 5)
        assert g.neighbors("A") == [("B", 5)]
        assert g.neighbors("B") == []  # B → A not added
        assert g.nodes == {"A", "B"}  # B still registered as node

    def test_isolated_target_is_in_graph(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        assert "B" in g
        assert len(g) == 2


class TestValidation:
    def test_negative_weight_raises(self):
        g = Graph()
        with pytest.raises(ValueError, match="від'ємних ваг"):
            g.add_edge("A", "B", -1)

    def test_zero_weight_allowed(self):
        g = Graph()
        g.add_edge("A", "B", 0)
        assert ("B", 0) in g.neighbors("A")

    def test_none_weight_raises_typeerror(self):
        g = Graph()
        with pytest.raises(TypeError, match="має бути числом"):
            g.add_edge("A", "B", None)

    def test_string_weight_raises_typeerror(self):
        g = Graph()
        with pytest.raises(TypeError, match="має бути числом"):
            g.add_edge("A", "B", "5")

    def test_bool_weight_raises_typeerror(self):
        """True/False — це int у Python, але як вага це майже завжди баг."""
        g = Graph()
        with pytest.raises(TypeError, match="має бути числом"):
            g.add_edge("A", "B", True)


class TestDefaultWeight:
    def test_no_weight_defaults_to_one(self):
        g = Graph()
        g.add_edge("A", "B")
        assert ("B", 1.0) in g.neighbors("A")

    def test_mixed_explicit_and_default(self):
        g = Graph()
        g.add_edge("A", "B")          # = 1.0
        g.add_edge("A", "C", 5)
        g.add_edge("B", "C", 2.5)
        assert ("B", 1.0) in g.neighbors("A")
        assert ("C", 5.0) in g.neighbors("A")
        assert ("C", 2.5) in g.neighbors("B")

    def test_int_weight_works(self):
        """Int та float ваги взаємозамінні через автоматичне промоутування в арифметиці."""
        g = Graph()
        g.add_edge("A", "B", 3)
        assert g.neighbors("A") == [("B", 3)]
        assert g.neighbors("A") == [("B", 3.0)]  # 3 == 3.0


class TestAddNode:
    def test_isolated_node(self):
        g = Graph()
        g.add_node("X")
        assert "X" in g
        assert g.neighbors("X") == []
        assert len(g) == 1

    def test_add_node_then_edge(self):
        g = Graph()
        g.add_node("A")
        g.add_edge("A", "B", 1)
        assert g.nodes == {"A", "B"}

    def test_add_node_idempotent(self):
        g = Graph()
        g.add_node("A")
        g.add_node("A")
        assert len(g) == 1


class TestNodesView:
    def test_nodes_is_live_view(self):
        """nodes повертає KeysView, який автоматично відображає зміни."""
        g = Graph()
        view = g.nodes
        assert len(view) == 0
        g.add_edge("A", "B")
        assert "A" in view and "B" in view  # view бачить нові вершини
        assert len(view) == 2

    def test_nodes_supports_set_operations(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert set(g.nodes) == {"A", "B", "C"}
        assert g.nodes & {"A", "X"} == {"A"}
