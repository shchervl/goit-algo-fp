"""Однозв'язний список: реверс, сортування злиттям, об'єднання двох відсортованих."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Optional


@dataclass(slots=True)
class Node:
    data: Any
    next: Optional["Node"] = None


class LinkedList:
    def __init__(self, values: Iterable | None = None) -> None:
        self.head: Optional[Node] = None
        if values is not None:
            self.extend(values)

    def append(self, value) -> None:
        node = Node(value)
        if self.head is None:
            self.head = node
            return
        cur = self.head
        while cur.next is not None:
            cur = cur.next
        cur.next = node

    def extend(self, values: Iterable) -> None:
        for v in values:
            self.append(v)

    def to_list(self) -> list:
        return list(self)

    def __iter__(self) -> Iterator:
        cur = self.head
        while cur is not None:
            yield cur.data
            cur = cur.next

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __repr__(self) -> str:
        return f"LinkedList({self.to_list()!r})"

    def reverse(self) -> None:
        """Реверсує список на місці, перевстановлюючи посилання між вузлами."""
        prev: Optional[Node] = None
        cur = self.head
        while cur is not None:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        self.head = prev

    def sort(self) -> None:
        """Сортує список на місці алгоритмом злиття (O(n log n))."""
        self.head = _merge_sort(self.head)


def _split(head: Node) -> tuple[Node, Optional[Node]]:
    """Розбиває список на дві приблизно рівні половини через slow/fast вказівники."""
    slow = head
    fast = head.next
    while fast is not None and fast.next is not None:
        slow = slow.next  # type: ignore[assignment]
        fast = fast.next.next
    second = slow.next
    slow.next = None
    return head, second


def _merge_nodes(a: Optional[Node], b: Optional[Node]) -> Optional[Node]:
    """Зливає два відсортовані ланцюжки вузлів у один відсортований."""
    dummy = Node(None)
    tail = dummy
    while a is not None and b is not None:
        if a.data <= b.data:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a if a is not None else b
    return dummy.next


def _merge_sort(head: Optional[Node]) -> Optional[Node]:
    if head is None or head.next is None:
        return head
    left_head, right_head = _split(head)
    return _merge_nodes(_merge_sort(left_head), _merge_sort(right_head))


def merge_sorted(a: LinkedList, b: LinkedList) -> LinkedList:
    """Об'єднує два відсортовані списки в новий відсортований список.

    Створює нові вузли, тож вхідні списки залишаються без змін.
    """
    result = LinkedList()
    i, j = a.head, b.head
    while i is not None and j is not None:
        if i.data <= j.data:
            result.append(i.data)
            i = i.next
        else:
            result.append(j.data)
            j = j.next
    while i is not None:
        result.append(i.data)
        i = i.next
    while j is not None:
        result.append(j.data)
        j = j.next
    return result
