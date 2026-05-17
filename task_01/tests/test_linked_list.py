import math
import random
from functools import total_ordering

import pytest

from task_01.linked_list import LinkedList, merge_sorted


class TestLinkedListBasics:
    def test_empty(self):
        ll = LinkedList()
        assert ll.to_list() == []
        assert len(ll) == 0
        assert ll.head is None

    def test_append_and_iterate(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll.to_list() == [1, 2, 3]

    def test_construct_from_iterable(self):
        ll = LinkedList([10, 20, 30])
        assert ll.to_list() == [10, 20, 30]
        assert len(ll) == 3


class TestReverse:
    def test_reverse_empty(self):
        ll = LinkedList()
        ll.reverse()
        assert ll.to_list() == []

    def test_reverse_single(self):
        ll = LinkedList([42])
        ll.reverse()
        assert ll.to_list() == [42]

    def test_reverse_two(self):
        ll = LinkedList([1, 2])
        ll.reverse()
        assert ll.to_list() == [2, 1]

    def test_reverse_many(self):
        ll = LinkedList([1, 2, 3, 4, 5])
        ll.reverse()
        assert ll.to_list() == [5, 4, 3, 2, 1]

    def test_reverse_twice_is_identity(self):
        original = [1, 2, 3, 4, 5]
        ll = LinkedList(original)
        ll.reverse()
        ll.reverse()
        assert ll.to_list() == original

    def test_reverse_rewires_existing_nodes(self):
        """Перевіряє, що реверс саме змінює посилання, а не створює нові вузли."""
        ll = LinkedList([1, 2, 3])
        nodes_before = []
        cur = ll.head
        while cur is not None:
            nodes_before.append(cur)
            cur = cur.next
        ll.reverse()
        nodes_after = []
        cur = ll.head
        while cur is not None:
            nodes_after.append(cur)
            cur = cur.next
        assert set(map(id, nodes_before)) == set(map(id, nodes_after))


class TestSort:
    def test_sort_empty(self):
        ll = LinkedList()
        ll.sort()
        assert ll.to_list() == []

    def test_sort_single(self):
        ll = LinkedList([7])
        ll.sort()
        assert ll.to_list() == [7]

    def test_sort_already_sorted(self):
        ll = LinkedList([1, 2, 3, 4, 5])
        ll.sort()
        assert ll.to_list() == [1, 2, 3, 4, 5]

    def test_sort_reversed(self):
        ll = LinkedList([5, 4, 3, 2, 1])
        ll.sort()
        assert ll.to_list() == [1, 2, 3, 4, 5]

    def test_sort_with_duplicates(self):
        ll = LinkedList([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])
        ll.sort()
        assert ll.to_list() == sorted([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])

    def test_sort_strings(self):
        ll = LinkedList(["banana", "apple", "cherry"])
        ll.sort()
        assert ll.to_list() == ["apple", "banana", "cherry"]

    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 42])
    def test_sort_random(self, seed):
        rng = random.Random(seed)
        data = [rng.randint(-100, 100) for _ in range(50)]
        ll = LinkedList(data)
        ll.sort()
        assert ll.to_list() == sorted(data)


class TestMergeSorted:
    def test_both_empty(self):
        result = merge_sorted(LinkedList(), LinkedList())
        assert result.to_list() == []

    def test_one_empty(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList()
        assert merge_sorted(a, b).to_list() == [1, 2, 3]
        assert merge_sorted(b, a).to_list() == [1, 2, 3]

    def test_interleaved(self):
        a = LinkedList([1, 3, 5, 7])
        b = LinkedList([2, 4, 6, 8])
        assert merge_sorted(a, b).to_list() == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_one_strictly_less(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList([10, 20, 30])
        assert merge_sorted(a, b).to_list() == [1, 2, 3, 10, 20, 30]

    def test_with_duplicates(self):
        a = LinkedList([1, 2, 2, 5])
        b = LinkedList([2, 3, 5, 5])
        assert merge_sorted(a, b).to_list() == [1, 2, 2, 2, 3, 5, 5, 5]

    def test_inputs_unmodified(self):
        a = LinkedList([1, 3, 5])
        b = LinkedList([2, 4, 6])
        merge_sorted(a, b)
        assert a.to_list() == [1, 3, 5]
        assert b.to_list() == [2, 4, 6]

    @pytest.mark.parametrize("seed", [0, 1, 7, 42])
    def test_merge_random(self, seed):
        rng = random.Random(seed)
        xs = sorted(rng.randint(-50, 50) for _ in range(20))
        ys = sorted(rng.randint(-50, 50) for _ in range(20))
        result = merge_sorted(LinkedList(xs), LinkedList(ys))
        assert result.to_list() == sorted(xs + ys)


class TestEmptyAndNoneConstruction:
    """Сценарії з порожніми списками та None як аргументом конструктора."""

    def test_construct_from_none(self):
        ll = LinkedList(None)
        assert ll.to_list() == []
        assert ll.head is None

    def test_construct_from_empty_list(self):
        ll = LinkedList([])
        assert ll.to_list() == []
        assert len(ll) == 0

    def test_construct_from_empty_tuple(self):
        ll = LinkedList(())
        assert ll.to_list() == []

    def test_append_to_freshly_empty(self):
        ll = LinkedList(None)
        ll.append(1)
        assert ll.to_list() == [1]
        assert ll.head is not None

    def test_extend_empty_iterable(self):
        ll = LinkedList([1, 2, 3])
        ll.extend([])
        assert ll.to_list() == [1, 2, 3]

    def test_merge_two_freshly_empty(self):
        result = merge_sorted(LinkedList(None), LinkedList(None))
        assert result.to_list() == []
        assert result.head is None


class TestNoneAsValues:
    """Сценарії, коли елементи списку самі є None."""

    def test_reverse_single_none(self):
        ll = LinkedList([None])
        ll.reverse()
        assert ll.to_list() == [None]

    def test_reverse_all_nones(self):
        ll = LinkedList([None, None, None])
        ll.reverse()
        assert ll.to_list() == [None, None, None]

    def test_reverse_mixed_with_none(self):
        ll = LinkedList([1, None, 2, None, 3])
        ll.reverse()
        assert ll.to_list() == [3, None, 2, None, 1]

    def test_sort_single_none_does_not_compare(self):
        ll = LinkedList([None])
        ll.sort()
        assert ll.to_list() == [None]

    def test_sort_multiple_nones_raises(self):
        ll = LinkedList([None, None])
        with pytest.raises(TypeError):
            ll.sort()

    def test_sort_none_mixed_with_int_raises(self):
        ll = LinkedList([1, None, 2])
        with pytest.raises(TypeError):
            ll.sort()

    def test_merge_with_none_values_raises(self):
        a = LinkedList([None])
        b = LinkedList([None])
        with pytest.raises(TypeError):
            merge_sorted(a, b)

    def test_merge_empty_with_none_values(self):
        """Якщо одна зі сторін порожня, порівняння None не відбувається."""
        a = LinkedList([None, None])
        b = LinkedList()
        assert merge_sorted(a, b).to_list() == [None, None]
        assert merge_sorted(b, a).to_list() == [None, None]


class TestDifferentDataTypes:
    """Сценарії з різними типами даних."""

    def test_reverse_floats(self):
        ll = LinkedList([1.5, 2.5, 3.5])
        ll.reverse()
        assert ll.to_list() == [3.5, 2.5, 1.5]

    def test_reverse_tuples(self):
        ll = LinkedList([(1, "a"), (2, "b"), (3, "c")])
        ll.reverse()
        assert ll.to_list() == [(3, "c"), (2, "b"), (1, "a")]

    def test_reverse_mixed_types(self):
        ll = LinkedList([1, "two", 3.0, (4,), None])
        ll.reverse()
        assert ll.to_list() == [None, (4,), 3.0, "two", 1]

    def test_sort_floats(self):
        ll = LinkedList([3.14, 1.41, 2.71, 0.58])
        ll.sort()
        assert ll.to_list() == [0.58, 1.41, 2.71, 3.14]

    def test_sort_int_and_float_mixed(self):
        ll = LinkedList([3, 1.5, 2, 0.5, 4])
        ll.sort()
        assert ll.to_list() == [0.5, 1.5, 2, 3, 4]

    def test_sort_booleans(self):
        ll = LinkedList([True, False, True, False])
        ll.sort()
        assert ll.to_list() == [False, False, True, True]

    def test_sort_tuples_lexicographic(self):
        ll = LinkedList([(2, 1), (1, 3), (2, 0), (1, 1)])
        ll.sort()
        assert ll.to_list() == [(1, 1), (1, 3), (2, 0), (2, 1)]

    def test_sort_incompatible_types_raises(self):
        ll = LinkedList([1, "two", 3])
        with pytest.raises(TypeError):
            ll.sort()

    def test_merge_floats(self):
        a = LinkedList([1.1, 3.3, 5.5])
        b = LinkedList([2.2, 4.4, 6.6])
        assert merge_sorted(a, b).to_list() == [1.1, 2.2, 3.3, 4.4, 5.5, 6.6]

    def test_merge_int_and_float(self):
        a = LinkedList([1, 3, 5])
        b = LinkedList([2.5, 4.5])
        assert merge_sorted(a, b).to_list() == [1, 2.5, 3, 4.5, 5]

    def test_merge_strings(self):
        a = LinkedList(["apple", "cherry"])
        b = LinkedList(["banana", "date"])
        assert merge_sorted(a, b).to_list() == ["apple", "banana", "cherry", "date"]

    def test_merge_tuples(self):
        a = LinkedList([(1, "a"), (3, "c")])
        b = LinkedList([(2, "b"), (4, "d")])
        assert merge_sorted(a, b).to_list() == [(1, "a"), (2, "b"), (3, "c"), (4, "d")]

    def test_merge_incompatible_types_raises(self):
        a = LinkedList([1, 2, 3])
        b = LinkedList(["a", "b", "c"])
        with pytest.raises(TypeError):
            merge_sorted(a, b)


class TestEmptyStrings:
    def test_reverse_with_empty_strings(self):
        ll = LinkedList(["", "a", "", "b", ""])
        ll.reverse()
        assert ll.to_list() == ["", "b", "", "a", ""]

    def test_reverse_all_empty_strings(self):
        ll = LinkedList(["", "", ""])
        ll.reverse()
        assert ll.to_list() == ["", "", ""]

    def test_sort_with_empty_strings(self):
        """Порожній рядок лексикографічно йде перед будь-яким непорожнім."""
        ll = LinkedList(["b", "", "a", "", "c"])
        ll.sort()
        assert ll.to_list() == ["", "", "a", "b", "c"]

    def test_sort_only_empty_strings(self):
        ll = LinkedList(["", "", ""])
        ll.sort()
        assert ll.to_list() == ["", "", ""]

    def test_merge_with_empty_strings(self):
        a = LinkedList(["", "b", "d"])
        b = LinkedList(["", "a", "c"])
        assert merge_sorted(a, b).to_list() == ["", "", "a", "b", "c", "d"]


class TestNestedStructures:
    def test_reverse_list_of_lists(self):
        ll = LinkedList([[1, 2], [3], [4, 5, 6]])
        ll.reverse()
        assert ll.to_list() == [[4, 5, 6], [3], [1, 2]]

    def test_reverse_nested_linked_lists(self):
        """Вузли можуть містити інші LinkedList — reverse не повинен їх торкатися."""
        inner_a = LinkedList([1, 2])
        inner_b = LinkedList([3, 4])
        ll = LinkedList([inner_a, inner_b])
        ll.reverse()
        out = ll.to_list()
        assert out[0] is inner_b
        assert out[1] is inner_a
        assert inner_a.to_list() == [1, 2]
        assert inner_b.to_list() == [3, 4]

    def test_sort_list_of_lists_lexicographic(self):
        ll = LinkedList([[3], [1, 2], [2], [1, 2, 3], [1]])
        ll.sort()
        assert ll.to_list() == [[1], [1, 2], [1, 2, 3], [2], [3]]

    def test_sort_deeply_nested(self):
        ll = LinkedList([[[2]], [[1]], [[3]]])
        ll.sort()
        assert ll.to_list() == [[[1]], [[2]], [[3]]]

    def test_merge_lists_of_lists(self):
        a = LinkedList([[1], [3, 0], [5]])
        b = LinkedList([[2], [4]])
        assert merge_sorted(a, b).to_list() == [[1], [2], [3, 0], [4], [5]]


@total_ordering
class Person:
    """Кастомний клас з порядком за віком через @total_ordering."""

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def __eq__(self, other):
        return isinstance(other, Person) and self.age == other.age

    def __lt__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return self.age < other.age

    def __hash__(self):
        return hash((self.name, self.age))

    def __repr__(self):
        return f"Person({self.name!r}, {self.age})"


class OnlyLE:
    """Мінімальний клас, що реалізує лише __le__ — саме його використовує merge."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __le__(self, other):
        if not isinstance(other, OnlyLE):
            return NotImplemented
        return self.value <= other.value

    def __repr__(self):
        return f"OnlyLE({self.value})"


class TestCustomComparable:
    def test_reverse_custom_objects(self):
        people = [Person("Alice", 30), Person("Bob", 25), Person("Carol", 40)]
        ll = LinkedList(people)
        ll.reverse()
        assert [p.name for p in ll] == ["Carol", "Bob", "Alice"]

    def test_sort_custom_objects_by_age(self):
        people = [
            Person("Carol", 40),
            Person("Alice", 30),
            Person("Bob", 25),
            Person("Dave", 35),
        ]
        ll = LinkedList(people)
        ll.sort()
        assert [p.name for p in ll] == ["Bob", "Alice", "Dave", "Carol"]
        assert [p.age for p in ll] == [25, 30, 35, 40]

    def test_merge_custom_objects(self):
        a = LinkedList([Person("A", 20), Person("B", 40), Person("C", 60)])
        b = LinkedList([Person("X", 30), Person("Y", 50)])
        result = merge_sorted(a, b)
        assert [p.age for p in result] == [20, 30, 40, 50, 60]

    def test_sort_with_only_le(self):
        """merge-sort використовує <=, тому достатньо __le__."""
        ll = LinkedList([OnlyLE(3), OnlyLE(1), OnlyLE(4), OnlyLE(1), OnlyLE(5)])
        ll.sort()
        assert [x.value for x in ll] == [1, 1, 3, 4, 5]

    def test_merge_with_only_le(self):
        a = LinkedList([OnlyLE(1), OnlyLE(3), OnlyLE(5)])
        b = LinkedList([OnlyLE(2), OnlyLE(4)])
        result = merge_sorted(a, b)
        assert [x.value for x in result] == [1, 2, 3, 4, 5]


class TestNaN:
    """NaN ламає інваріант впорядкованості: nan <= x та x <= nan завжди False.
    Тому ми не перевіряємо точний порядок, а перевіряємо інваріанти, які мають триматися."""

    def test_reverse_with_nan(self):
        """Reverse не порівнює — має працювати без сюрпризів."""
        nan = float("nan")
        ll = LinkedList([1.0, nan, 2.0, nan, 3.0])
        ll.reverse()
        out = ll.to_list()
        assert out[0] == 3.0
        assert math.isnan(out[1])
        assert out[2] == 2.0
        assert math.isnan(out[3])
        assert out[4] == 1.0

    def test_sort_only_nans_preserves_count(self):
        nan = float("nan")
        ll = LinkedList([nan, nan, nan])
        ll.sort()
        out = ll.to_list()
        assert len(out) == 3
        assert all(math.isnan(x) for x in out)

    def test_sort_mixed_nan_preserves_multiset_but_order_undefined(self):
        """Sort не падає і не губить/не вигадує значень, але порядок з NaN — undefined.

        NaN порівнюється як False з усім (включно з самим собою), тому merge-sort не
        здатен побудувати коректний порядок. Гарантуємо лише збереження мультимножини:
        ту саму кількість NaN та той самий мультимножинний набір скінченних значень.
        """
        nan = float("nan")
        data = [3.0, nan, 1.0, nan, 2.0, nan, 0.0]
        ll = LinkedList(data)
        ll.sort()
        out = ll.to_list()
        assert len(out) == len(data)
        assert sum(1 for x in out if math.isnan(x)) == 3
        finite_in = sorted(x for x in data if not math.isnan(x))
        finite_out = sorted(x for x in out if not math.isnan(x))
        assert finite_in == finite_out

    def test_merge_finite_with_nan_side(self):
        """Якщо один зі списків — лише NaN, поведінка детермінована для непорівнянь."""
        nan = float("nan")
        a = LinkedList([1.0, 2.0, 3.0])
        b = LinkedList([nan])
        out = merge_sorted(a, b).to_list()
        assert len(out) == 4
        assert sum(1 for x in out if math.isnan(x)) == 1
        finite = [x for x in out if not math.isnan(x)]
        assert finite == [1.0, 2.0, 3.0]

    def test_merge_empty_with_nan(self):
        nan = float("nan")
        a = LinkedList([nan, nan])
        b = LinkedList()
        out = merge_sorted(a, b).to_list()
        assert len(out) == 2
        assert all(math.isnan(x) for x in out)
