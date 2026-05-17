import math

import pytest

from task_03.dijkstra import dijkstra, reconstruct_path
from task_03.graph import Graph


def _make(edges, directed=False):
    g = Graph(directed=directed)
    for u, v, w in edges:
        g.add_edge(u, v, w)
    return g


class TestDijkstraBasics:
    def test_invalid_start_raises(self):
        g = _make([("A", "B", 1)])
        with pytest.raises(ValueError, match="відсутня"):
            dijkstra(g, "Z")

    def test_single_node(self):
        g = Graph()
        g.add_edge("A", "A", 0)  # self-loop forces A to register
        distances, predecessors = dijkstra(g, "A")
        assert distances == {"A": 0.0}
        assert predecessors == {"A": None}

    def test_two_nodes(self):
        g = _make([("A", "B", 3)])
        distances, predecessors = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 3.0}
        assert predecessors == {"A": None, "B": "A"}

    def test_start_distance_is_zero(self):
        g = _make([("A", "B", 5), ("B", "C", 5)])
        distances, _ = dijkstra(g, "A")
        assert distances["A"] == 0.0


class TestClassicExample:
    """Класичний приклад з Вікіпедії: 6 вершин, 9 ребер."""

    EDGES = [
        ("A", "B", 7), ("A", "C", 9), ("A", "F", 14),
        ("B", "C", 10), ("B", "D", 15),
        ("C", "D", 11), ("C", "F", 2),
        ("D", "E", 6),
        ("E", "F", 9),
    ]

    def test_distances_from_A(self):
        g = _make(self.EDGES)
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 7.0, "C": 9.0, "D": 20.0, "E": 20.0, "F": 11.0}

    def test_paths_from_A(self):
        g = _make(self.EDGES)
        _, predecessors = dijkstra(g, "A")
        assert reconstruct_path(predecessors, "A") == ["A"]
        assert reconstruct_path(predecessors, "B") == ["A", "B"]
        assert reconstruct_path(predecessors, "C") == ["A", "C"]
        assert reconstruct_path(predecessors, "D") == ["A", "C", "D"]
        assert reconstruct_path(predecessors, "E") == ["A", "C", "F", "E"]
        assert reconstruct_path(predecessors, "F") == ["A", "C", "F"]

    def test_distances_from_E(self):
        """Симетричність — у неорієнтованому графі d(A,E) == d(E,A)."""
        g = _make(self.EDGES)
        distances, _ = dijkstra(g, "E")
        assert distances["A"] == 20.0


class TestDirectedGraph:
    def test_one_way_path(self):
        g = _make([("A", "B", 1), ("B", "C", 1)], directed=True)
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 1.0, "C": 2.0}

    def test_no_path_back(self):
        """A→B→C існує, але C→B немає у directed графі."""
        g = _make([("A", "B", 1), ("B", "C", 1)], directed=True)
        distances, _ = dijkstra(g, "C")
        assert distances == {"C": 0.0}

    def test_directed_chooses_shorter_path(self):
        g = _make([
            ("A", "B", 1), ("B", "D", 10),
            ("A", "C", 5), ("C", "D", 1),
        ], directed=True)
        distances, predecessors = dijkstra(g, "A")
        assert distances["D"] == 6.0
        assert reconstruct_path(predecessors, "D") == ["A", "C", "D"]


class TestUnreachable:
    def test_disconnected_component(self):
        """B-C ізольована від A."""
        g = _make([("A", "X", 1), ("B", "C", 2)])
        distances, predecessors = dijkstra(g, "A")
        assert distances == {"A": 0.0, "X": 1.0}
        assert "B" not in distances
        assert "C" not in distances

    def test_reconstruct_path_unreachable_returns_empty(self):
        g = _make([("A", "X", 1), ("B", "C", 2)])
        _, predecessors = dijkstra(g, "A")
        assert reconstruct_path(predecessors, "B") == []
        assert reconstruct_path(predecessors, "C") == []

    def test_directed_unreachable(self):
        g = _make([("A", "B", 1), ("C", "D", 1)], directed=True)
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 1.0}


class TestParallelEdgesAndLoops:
    def test_parallel_edges_uses_shortest(self):
        """Два ребра A↔B різної ваги — має взятись коротше."""
        g = Graph()
        g.add_edge("A", "B", 10)
        g.add_edge("A", "B", 3)
        distances, _ = dijkstra(g, "A")
        assert distances["B"] == 3.0

    def test_self_loop_does_not_break(self):
        g = _make([("A", "A", 5), ("A", "B", 2)])
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 2.0}

    def test_zero_weight_edges(self):
        g = _make([("A", "B", 0), ("B", "C", 0)])
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 0.0, "C": 0.0}


class TestStaleEntriesSkipped:
    """Перевірка коректності lazy-deletion: коли краща вага знайдена пізніше,
    старі stale-записи мають бути проігноровані без помилкових оновлень."""

    def test_relaxation_through_longer_first_then_shorter(self):
        # A→B напряму 10; A→C→B = 1+2=3. Дейкстра має вибрати 3.
        g = _make([("A", "B", 10), ("A", "C", 1), ("C", "B", 2)])
        distances, predecessors = dijkstra(g, "A")
        assert distances["B"] == 3.0
        assert reconstruct_path(predecessors, "B") == ["A", "C", "B"]

    def test_dense_chain(self):
        # Великий шлях де треба багато релаксацій
        edges = [(str(i), str(i + 1), 1) for i in range(20)]
        g = _make(edges)
        distances, _ = dijkstra(g, "0")
        assert distances["20"] == 20.0


class TestReconstructPath:
    def test_path_to_start_is_just_start(self):
        predecessors = {"A": None, "B": "A"}
        assert reconstruct_path(predecessors, "A") == ["A"]

    def test_multi_step_path(self):
        predecessors = {"A": None, "B": "A", "C": "B", "D": "C"}
        assert reconstruct_path(predecessors, "D") == ["A", "B", "C", "D"]

    def test_missing_target_returns_empty(self):
        assert reconstruct_path({"A": None}, "Z") == []


class TestNumericTypes:
    def test_float_weights(self):
        g = _make([("A", "B", 1.5), ("B", "C", 2.25)])
        distances, _ = dijkstra(g, "A")
        assert distances["C"] == pytest.approx(3.75)

    def test_int_weights_return_float_distances(self):
        g = _make([("A", "B", 3)])
        distances, _ = dijkstra(g, "A")
        assert isinstance(distances["B"], float)
        assert distances["B"] == 3.0


class TestNumericNodeIds:
    """Вершини можуть бути будь-якими hashable, не лише рядками."""

    def test_integer_nodes(self):
        g = _make([(1, 2, 4), (2, 3, 5), (1, 3, 100)])
        distances, predecessors = dijkstra(g, 1)
        assert distances == {1: 0.0, 2: 4.0, 3: 9.0}
        assert reconstruct_path(predecessors, 3) == [1, 2, 3]

    def test_tuple_nodes(self):
        """Координати на сітці як вершини."""
        g = _make([
            ((0, 0), (1, 0), 1.0),
            ((1, 0), (1, 1), 1.0),
            ((0, 0), (1, 1), 3.0),
        ])
        distances, _ = dijkstra(g, (0, 0))
        assert distances[(1, 1)] == 2.0


class TestCycles:
    def test_undirected_triangle(self):
        """A↔B↔C↔A — найкоротший до C напряму, а не через B."""
        g = _make([("A", "B", 1), ("B", "C", 1), ("C", "A", 1)])
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 1.0, "C": 1.0}

    def test_directed_cycle_terminates(self):
        """A→B→C→A — Дейкстра має завершитись і дати правильні відстані."""
        g = _make([("A", "B", 1), ("B", "C", 1), ("C", "A", 1)], directed=True)
        distances, _ = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 1.0, "C": 2.0}

    def test_directed_cycle_with_shortcut(self):
        """Довший цикл плюс прямий шорткат — має вибрати шорткат."""
        g = _make([
            ("A", "B", 100),
            ("B", "C", 1), ("C", "D", 1), ("D", "E", 1), ("E", "A", 1),
            ("A", "C", 2),
        ], directed=True)
        distances, predecessors = dijkstra(g, "A")
        assert distances["C"] == 2.0
        assert reconstruct_path(predecessors, "C") == ["A", "C"]
        assert distances["B"] == 100.0  # єдиний шлях


class TestNoneAsNode:
    def test_none_as_node_id(self):
        g = _make([(None, "A", 1), ("A", "B", 2)])
        distances, _ = dijkstra(g, None)
        assert distances == {None: 0.0, "A": 1.0, "B": 3.0}

    def test_none_start_when_missing_raises(self):
        g = _make([("A", "B", 1)])
        with pytest.raises(ValueError, match="відсутня"):
            dijkstra(g, None)


class TestStartHasNoOutgoing:
    def test_directed_start_with_no_outgoing_edges(self):
        """В орієнтованому графі: B приймає ребро A→B, але сам нічого не має."""
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        distances, predecessors = dijkstra(g, "B")
        assert distances == {"B": 0.0}
        assert predecessors == {"B": None}


class TestTiedPaths:
    def test_equal_weight_paths_give_deterministic_distance(self):
        """Два шляхи однакової ваги (A→B→D = A→C→D = 2). Відстань завжди 2.0;
        шлях — будь-який з валідних."""
        g = _make([
            ("A", "B", 1), ("A", "C", 1),
            ("B", "D", 1), ("C", "D", 1),
        ])
        distances, predecessors = dijkstra(g, "A")
        assert distances["D"] == 2.0
        path = reconstruct_path(predecessors, "D")
        assert path in (["A", "B", "D"], ["A", "C", "D"])


class TestNegativeWeightInDirected:
    def test_directed_graph_validates_too(self):
        g = Graph(directed=True)
        with pytest.raises(ValueError, match="від'ємних ваг"):
            g.add_edge("A", "B", -1)


class TestReconstructPathEdgeCases:
    def test_empty_predecessors(self):
        assert reconstruct_path({}, "A") == []

    def test_only_start_in_predecessors(self):
        assert reconstruct_path({"A": None}, "A") == ["A"]


class TestLargerGraph:
    def test_linear_chain_100_nodes(self):
        edges = [(i, i + 1, 1) for i in range(100)]
        g = _make(edges)
        distances, predecessors = dijkstra(g, 0)
        assert distances[100] == 100.0
        assert reconstruct_path(predecessors, 100) == list(range(101))


class TestUnweightedGraph:
    """Дефолтна вага 1.0 → Дейкстра поводиться як BFS: рахує кількість стрибків."""

    def test_unweighted_distances_count_hops(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "D")
        g.add_edge("A", "D")  # шорткат за 1 стрибок
        distances, predecessors = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 1.0, "C": 2.0, "D": 1.0}
        assert reconstruct_path(predecessors, "D") == ["A", "D"]


class TestDijkstraResultAPI:
    """NamedTuple підтримує і tuple-unpacking, і attribute access, і path_to()."""

    def test_tuple_unpacking_backward_compat(self):
        g = _make([("A", "B", 3)])
        distances, predecessors = dijkstra(g, "A")
        assert distances == {"A": 0.0, "B": 3.0}
        assert predecessors == {"A": None, "B": "A"}

    def test_attribute_access(self):
        g = _make([("A", "B", 3)])
        result = dijkstra(g, "A")
        assert result.distances == {"A": 0.0, "B": 3.0}
        assert result.predecessors == {"A": None, "B": "A"}

    def test_path_to_method(self):
        g = _make([("A", "B", 3), ("B", "C", 4)])
        result = dijkstra(g, "A")
        assert result.path_to("C") == ["A", "B", "C"]
        assert result.path_to("A") == ["A"]
        assert result.path_to("Z") == []  # недосяжний
