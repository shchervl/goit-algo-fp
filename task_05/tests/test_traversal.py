import pytest

from task_04.heap_tree import Node
from task_05.traversal import (
    DARK_RGB,
    LIGHT_RGB,
    apply_traversal_colors,
    bfs_iterative,
    dfs_iterative,
    draw_traversal,
    reset_colors,
    shade_gradient,
)


def _make_full_seven() -> Node:
    """    1
          / \\
         2   3
        / \\ / \\
       4  5 6  7
    """
    root = Node(1)
    root.left = Node(2)
    root.right = Node(3)
    root.left.left = Node(4)
    root.left.right = Node(5)
    root.right.left = Node(6)
    root.right.right = Node(7)
    return root


def _make_left_skewed_three() -> Node:
    """1 → 2 (left) → 3 (left). Right гілки немає."""
    root = Node(1)
    root.left = Node(2)
    root.left.left = Node(3)
    return root


class TestDFS:
    def test_empty(self):
        assert dfs_iterative(None) == []

    def test_single_node(self):
        n = Node(42)
        assert [x.val for x in dfs_iterative(n)] == [42]

    def test_full_balanced(self):
        """Pre-order: корінь, ліве піддерево, праве піддерево."""
        root = _make_full_seven()
        assert [n.val for n in dfs_iterative(root)] == [1, 2, 4, 5, 3, 6, 7]

    def test_left_skewed(self):
        root = _make_left_skewed_three()
        assert [n.val for n in dfs_iterative(root)] == [1, 2, 3]

    def test_right_skewed(self):
        root = Node(1)
        root.right = Node(2)
        root.right.right = Node(3)
        assert [n.val for n in dfs_iterative(root)] == [1, 2, 3]

    def test_only_left_subtree_has_children(self):
        root = Node(1)
        root.left = Node(2)
        root.right = Node(3)
        root.left.left = Node(4)
        root.left.right = Node(5)
        # DFS pre-order: 1, 2, 4, 5, 3
        assert [n.val for n in dfs_iterative(root)] == [1, 2, 4, 5, 3]


class TestBFS:
    def test_empty(self):
        assert bfs_iterative(None) == []

    def test_single_node(self):
        n = Node(42)
        assert [x.val for x in bfs_iterative(n)] == [42]

    def test_full_balanced(self):
        """Level-order: 1 / 2,3 / 4,5,6,7."""
        root = _make_full_seven()
        assert [n.val for n in bfs_iterative(root)] == [1, 2, 3, 4, 5, 6, 7]

    def test_left_skewed(self):
        root = _make_left_skewed_three()
        assert [n.val for n in bfs_iterative(root)] == [1, 2, 3]

    def test_incomplete_last_level(self):
        """1 / 2,3 / 4,5 (без правих дітей у 3)."""
        root = Node(1)
        root.left = Node(2)
        root.right = Node(3)
        root.left.left = Node(4)
        root.left.right = Node(5)
        assert [n.val for n in bfs_iterative(root)] == [1, 2, 3, 4, 5]


class TestShadeGradient:
    def test_empty(self):
        assert shade_gradient(0) == []

    def test_single_returns_dark(self):
        colors = shade_gradient(1)
        assert len(colors) == 1
        # перший = темний
        r, g, b = DARK_RGB
        assert colors[0] == f"#{r:02x}{g:02x}{b:02x}"

    def test_two_endpoints(self):
        colors = shade_gradient(2)
        r, g, b = DARK_RGB
        R, G, B = LIGHT_RGB
        assert colors[0] == f"#{r:02x}{g:02x}{b:02x}"
        assert colors[1] == f"#{R:02x}{G:02x}{B:02x}"

    def test_all_unique(self):
        colors = shade_gradient(7)
        assert len(set(colors)) == 7  # всі різні

    def test_hex_format(self):
        for c in shade_gradient(5):
            assert c.startswith("#")
            assert len(c) == 7  # # + 6 hex
            int(c[1:], 16)  # парситься як hex

    def test_monotonic_dark_to_light(self):
        """Кожна наступна RGB-сума має бути >= попередньої (від темного до світлого)."""
        colors = shade_gradient(10)
        sums = [int(c[1:3], 16) + int(c[3:5], 16) + int(c[5:7], 16) for c in colors]
        for i in range(len(sums) - 1):
            assert sums[i] <= sums[i + 1]


class TestApplyTraversalColors:
    def test_empty_sequence_no_op(self):
        apply_traversal_colors([])  # не падає

    def test_single_node_gets_dark(self):
        n = Node(1)
        apply_traversal_colors([n])
        r, g, b = DARK_RGB
        assert n.color == f"#{r:02x}{g:02x}{b:02x}"

    def test_modifies_in_place(self):
        root = _make_full_seven()
        seq = dfs_iterative(root)
        apply_traversal_colors(seq)
        # перший вузол послідовності — темніший за останній (за RGB-сумою)
        first_sum = sum(int(seq[0].color[i:i+2], 16) for i in (1, 3, 5))
        last_sum = sum(int(seq[-1].color[i:i+2], 16) for i in (1, 3, 5))
        assert first_sum < last_sum

    def test_all_nodes_get_unique_colors(self):
        root = _make_full_seven()
        seq = bfs_iterative(root)
        apply_traversal_colors(seq)
        colors = [n.color for n in seq]
        assert len(set(colors)) == len(seq)


class TestResetColors:
    def test_empty_no_op(self):
        reset_colors(None)

    def test_resets_all_to_default(self):
        root = _make_full_seven()
        apply_traversal_colors(dfs_iterative(root))
        reset_colors(root)
        for n in dfs_iterative(root):
            assert n.color == "skyblue"

    def test_custom_color(self):
        root = _make_full_seven()
        reset_colors(root, color="red")
        for n in dfs_iterative(root):
            assert n.color == "red"


class TestDrawTraversalSmoke:
    @pytest.fixture(autouse=True)
    def _agg_backend(self):
        import matplotlib

        matplotlib.use("Agg")

    def test_returns_sequence_dfs(self, tmp_path):
        root = _make_full_seven()
        seq = draw_traversal(root, order="dfs", save=str(tmp_path / "dfs.png"))
        assert [n.val for n in seq] == [1, 2, 4, 5, 3, 6, 7]

    def test_returns_sequence_bfs(self, tmp_path):
        root = _make_full_seven()
        seq = draw_traversal(root, order="bfs", save=str(tmp_path / "bfs.png"))
        assert [n.val for n in seq] == [1, 2, 3, 4, 5, 6, 7]

    def test_invalid_order_raises(self):
        with pytest.raises(ValueError, match="невідомий order"):
            draw_traversal(_make_full_seven(), order="zigzag")  # type: ignore[arg-type]

    def test_empty_returns_empty(self):
        assert draw_traversal(None) == []

    def test_save_png(self, tmp_path):
        out = tmp_path / "dfs.png"
        draw_traversal(_make_full_seven(), order="dfs", save=str(out))
        assert out.exists() and out.stat().st_size > 0

    def test_nodes_colored_after_traversal(self, tmp_path):
        root = _make_full_seven()
        draw_traversal(root, order="bfs", save=str(tmp_path / "bfs.png"))
        for n in bfs_iterative(root):
            assert n.color.startswith("#")
            assert len(n.color) == 7
