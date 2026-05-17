import pytest

from task_04.heap_tree import (
    Node,
    _build_graph,
    _layout,
    _validate_min_heap,
    build_tree_from_heap,
    draw_heap,
)


class TestNode:
    def test_default_color(self):
        n = Node(5)
        assert n.val == 5
        assert n.color == "skyblue"
        assert n.left is None
        assert n.right is None
        assert n.id  # uuid непорожній

    def test_custom_color(self):
        n = Node("X", color="red")
        assert n.color == "red"
        assert n.val == "X"

    def test_unique_ids_for_duplicate_values(self):
        a = Node(1)
        b = Node(1)
        assert a.id != b.id


class TestBuildTreeFromHeap:
    def test_empty_returns_none(self):
        assert build_tree_from_heap([]) is None

    def test_none_returns_none(self):
        assert build_tree_from_heap(None) is None  # falsy

    def test_single_node(self):
        root = build_tree_from_heap([5])
        assert root.val == 5
        assert root.left is None and root.right is None

    def test_full_tree_seven_nodes(self):
        root = build_tree_from_heap([1, 2, 3, 4, 5, 6, 7])
        assert root.val == 1
        assert root.left.val == 2 and root.right.val == 3
        assert root.left.left.val == 4 and root.left.right.val == 5
        assert root.right.left.val == 6 and root.right.right.val == 7
        assert root.left.left.left is None

    def test_incomplete_last_level(self):
        """[1,2,3,4,5] — у правого нащадка кореня немає дітей."""
        root = build_tree_from_heap([1, 2, 3, 4, 5])
        assert root.left.left.val == 4
        assert root.left.right.val == 5
        assert root.right.left is None
        assert root.right.right is None

    def test_color_fn_applied(self):
        def color(idx: int, val) -> str:
            return "red" if idx == 0 else "blue"

        root = build_tree_from_heap([1, 2, 3], color_fn=color)
        assert root.color == "red"
        assert root.left.color == "blue"
        assert root.right.color == "blue"

    def test_color_fn_can_use_value(self):
        def by_parity(_idx: int, val: int) -> str:
            return "lightgreen" if val % 2 == 0 else "lightyellow"

        root = build_tree_from_heap([2, 3, 4], color_fn=by_parity)
        assert root.color == "lightgreen"
        assert root.left.color == "lightyellow"
        assert root.right.color == "lightgreen"

    def test_validate_passes_valid_heap(self):
        # після heapq.heapify([10,4,5,1,3,7,2,8,6,9])
        build_tree_from_heap([1, 3, 2, 4, 9, 7, 5, 8, 6, 10], validate=True)

    def test_validate_raises_on_invalid_heap(self):
        with pytest.raises(ValueError, match="не min-heap"):
            build_tree_from_heap([10, 5, 3, 1], validate=True)

    def test_no_validation_silently_accepts_invalid(self):
        """validate=False (default) дозволяє будь-який масив — caller відповідає."""
        root = build_tree_from_heap([10, 5, 3, 1])  # not a heap
        assert root.val == 10  # ніяких помилок


class TestValidateMinHeap:
    def test_empty_passes(self):
        _validate_min_heap([])

    def test_single_passes(self):
        _validate_min_heap([42])

    def test_valid_heap_passes(self):
        _validate_min_heap([1, 3, 2, 4, 9, 7, 5])

    def test_violation_at_left_child(self):
        with pytest.raises(ValueError, match=r"heap\[0\]=5.*heap\[1\]=3"):
            _validate_min_heap([5, 3, 10])

    def test_violation_at_right_child(self):
        with pytest.raises(ValueError, match=r"heap\[0\]=5.*heap\[2\]=2"):
            _validate_min_heap([5, 10, 2])

    def test_violation_deep_in_tree(self):
        with pytest.raises(ValueError):
            _validate_min_heap([1, 2, 3, 4, 5, 6, 0])  # heap[2]=3 > heap[6]=0


class TestLayout:
    def test_single_node_at_origin(self):
        root = build_tree_from_heap([1])
        pos = _layout(root)
        assert pos[root.id] == (0.0, 0.0)

    def test_y_decreases_by_level(self):
        root = build_tree_from_heap([1, 2, 3, 4, 5])
        pos = _layout(root)
        assert pos[root.id][1] == 0
        assert pos[root.left.id][1] == -1
        assert pos[root.left.left.id][1] == -2

    def test_left_is_negative_x_right_is_positive(self):
        root = build_tree_from_heap([1, 2, 3])
        pos = _layout(root)
        assert pos[root.left.id][0] < 0
        assert pos[root.right.id][0] > 0

    def test_symmetric_x_for_siblings(self):
        root = build_tree_from_heap([1, 2, 3])
        pos = _layout(root)
        assert pos[root.left.id][0] == -pos[root.right.id][0]

    def test_parent_is_midpoint_of_children(self):
        root = build_tree_from_heap([1, 2, 3, 4, 5, 6, 7])
        pos = _layout(root)
        assert pos[root.id][0] == (pos[root.left.id][0] + pos[root.right.id][0]) / 2
        assert pos[root.left.id][0] == (
            pos[root.left.left.id][0] + pos[root.left.right.id][0]
        ) / 2

    def test_leaves_are_evenly_spaced(self):
        root = build_tree_from_heap([1, 2, 3, 4, 5, 6, 7])
        pos = _layout(root)
        leaves = [root.left.left, root.left.right, root.right.left, root.right.right]
        xs = sorted(pos[leaf.id][0] for leaf in leaves)
        diffs = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
        assert all(abs(d - 1.0) < 1e-9 for d in diffs)

    def test_tree_centered_horizontally(self):
        root = build_tree_from_heap([1, 2, 3, 4, 5])
        pos = _layout(root)
        xs = [p[0] for p in pos.values()]
        assert abs(min(xs) + max(xs)) < 1e-9  # центр у 0


class TestBuildGraph:
    def test_single_node(self):
        root = build_tree_from_heap([5])
        g = _build_graph(root)
        assert len(g.nodes) == 1
        assert len(g.edges) == 0

    def test_full_tree_has_n_minus_1_edges(self):
        root = build_tree_from_heap([1, 2, 3, 4, 5, 6, 7])
        g = _build_graph(root)
        assert len(g.nodes) == 7
        assert len(g.edges) == 6

    def test_node_attributes_stored(self):
        root = build_tree_from_heap([42])
        g = _build_graph(root)
        data = dict(g.nodes(data=True))
        assert data[root.id]["label"] == 42
        assert data[root.id]["color"] == "skyblue"

    def test_edges_connect_parent_to_children(self):
        root = build_tree_from_heap([1, 2, 3])
        g = _build_graph(root)
        assert (root.id, root.left.id) in g.edges
        assert (root.id, root.right.id) in g.edges


class TestDuplicateValues:
    """Дублікати у купі — id мають бути унікальними, граф має повну кількість вузлів."""

    def test_all_duplicates(self):
        root = build_tree_from_heap([1, 1, 1, 1, 1])
        g = _build_graph(root)
        assert len(g.nodes) == 5  # 5 окремих id попри однакові val
        labels = {data["label"] for _, data in g.nodes(data=True)}
        assert labels == {1}


class TestDrawHeapSmoke:
    def test_empty_heap_returns_silently(self, capsys):
        result = draw_heap([])
        assert result is None
        captured = capsys.readouterr()
        assert captured.out == ""  # ніяких print

    def test_save_png_no_print(self, tmp_path, capsys):
        import matplotlib

        matplotlib.use("Agg")
        out = tmp_path / "heap.png"
        draw_heap([3, 1, 4, 1, 5, 9, 2, 6], save=str(out))
        assert out.exists() and out.stat().st_size > 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_validate_propagates_through_draw_heap(self):
        with pytest.raises(ValueError, match="не min-heap"):
            draw_heap([10, 5, 3], validate=True)
