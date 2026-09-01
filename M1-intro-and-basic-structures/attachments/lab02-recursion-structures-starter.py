#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 2. Рекурсивные функции; динамический массив, стек и дек — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-02 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab02-recursion-structures-starter.py --variant N
"""
from __future__ import annotations

import argparse
import collections
import math
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Рекурсивные функции (счётчик вызовов — для сравнения наивной рекурсии
#    и мемоизации; результаты счётчика включаются в отчёт)
# ---------------------------------------------------------------------------

CALLS = {"fib_naive": 0, "fib_memo": 0}  # счётчики рекурсивных вызовов


def factorial(n: int) -> int:
    """Факториал n >= 0 рекурсивно. Ожидаемая сложность: TODO (обосновать в отчёте)."""
    # TODO: базовое условие + рекурсивный переход
    raise NotImplementedError


def fib_naive(n: int) -> int:
    """n-е число Фибоначчи наивной рекурсией; увеличивает CALLS["fib_naive"].

    Ожидаемая сложность: TODO (экспоненциальная — показать счётчиком вызовов).
    """
    CALLS["fib_naive"] += 1
    # TODO: F(0)=0, F(1)=1, далее F(n)=F(n-1)+F(n-2)
    raise NotImplementedError


def fib_memo(n: int, memo: dict[int, int] | None = None) -> int:
    """n-е число Фибоначчи с мемоизацией; увеличивает CALLS["fib_memo"].

    Ожидаемая сложность: TODO (линейная — сравнить счётчики в отчёте).
    """
    CALLS["fib_memo"] += 1
    # TODO: словарь memo передаётся по рекурсии; повторные подзадачи не пересчитываются
    raise NotImplementedError


def hanoi(n: int, src: str = "A", dst: str = "C", aux: str = "B") -> int:
    """Ханойские башни: вернуть число перемещений n дисков (src -> dst).

    Проверка в self_check: число перемещений равно 2**n - 1.
    """
    # TODO: базовое условие n == 0; иначе перенести n-1 на aux, 1 на dst, n-1 на dst
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Динамический массив с ручным управлением ёмкостью (рост x2)
# ---------------------------------------------------------------------------


class DynamicArray:
    """Динамический массив поверх «сырого» буфера фиксированной ёмкости.

    Инвариант: 0 <= self._size <= self._capacity.
    Буфер имитируем списком фиксированной длины, заполненным None;
    использовать list.append/insert для буфера запрещено.
    """

    INITIAL_CAPACITY = 4

    def __init__(self) -> None:
        self._capacity = self.INITIAL_CAPACITY
        self._size = 0
        self._buffer: list = [None] * self._capacity  # «сырая» память

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _grow(self) -> None:
        """Увеличить ёмкость в 2 раза и скопировать элементы в новый буфер."""
        # TODO: выделить новый буфер размера 2 * capacity, перенести _size элементов
        raise NotImplementedError

    def append(self, value) -> None:
        """Добавить элемент в конец; при size == capacity сначала вызвать _grow.

        Амортизированная сложность: TODO (обосновать методом учёта в отчёте).
        """
        # TODO: рост при необходимости, запись в ячейку _buffer[_size], инкремент _size
        raise NotImplementedError

    def get(self, index: int):
        """Вернуть элемент по индексу 0 <= index < size; иначе IndexError."""
        # TODO: проверка границ + чтение из буфера
        raise NotImplementedError

    def set(self, index: int, value) -> None:
        """Записать элемент по индексу 0 <= index < size; иначе IndexError."""
        # TODO: проверка границ + запись в буфер
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Стек и дек на базе собственных структур
# ---------------------------------------------------------------------------


class Stack:
    """Стек (LIFO) на базе DynamicArray."""

    def __init__(self) -> None:
        self._data = DynamicArray()

    def __len__(self) -> int:
        return len(self._data)

    def push(self, value) -> None:
        """Положить элемент на вершину. Амортизированная сложность: TODO."""
        # TODO: делегировать DynamicArray.append
        raise NotImplementedError

    def pop(self):
        """Снять элемент с вершины; для пустого стека — IndexError."""
        # TODO: прочитать последний элемент, уменьшить размер
        raise NotImplementedError

    def peek(self):
        """Вернуть вершину без удаления; для пустого стека — IndexError."""
        # TODO
        raise NotImplementedError


class _Node:
    """Узел двусвязного списка для Deque."""

    __slots__ = ("value", "prev", "next")

    def __init__(self, value, prev=None, next=None) -> None:  # noqa: A002
        self.value = value
        self.prev = prev
        self.next = next


class Deque:
    """Дек (двусторонняя очередь) на базе двусвязного списка.

    Все четыре операции концов должны стоить O(1) — без амортизации,
    в отличие от вставки в начало динамического массива (см. отчёт).
    """

    def __init__(self) -> None:
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push_front(self, value) -> None:
        """Добавить элемент в начало. Сложность: TODO."""
        # TODO: создать узел, перевязать ссылки head (учесть пустой дек)
        raise NotImplementedError

    def push_back(self, value) -> None:
        """Добавить элемент в конец. Сложность: TODO."""
        # TODO: симметрично push_front для tail
        raise NotImplementedError

    def pop_front(self):
        """Извлечь элемент из начала; для пустого дека — IndexError."""
        # TODO: учесть переход к пустому деку (tail тоже обнуляется)
        raise NotImplementedError

    def pop_back(self):
        """Извлечь элемент из конца; для пустого дека — IndexError."""
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные и типовые случаи + сверка с эталонами стандартной библиотеки."""
    # --- рекурсия: сверка с math.factorial и формулой Ханойских башен ---
    assert factorial(0) == 1
    for n in range(0, 12):
        assert factorial(n) == math.factorial(n)
    CALLS["fib_naive"] = CALLS["fib_memo"] = 0
    assert fib_naive(10) == 55
    assert fib_memo(10) == 55
    assert CALLS["fib_memo"] < CALLS["fib_naive"]  # мемоизация экономит вызовы
    for n in (0, 1, 3, 8):
        assert hanoi(n) == 2 ** n - 1

    # --- DynamicArray: инвариант size <= capacity, сверка с list ---
    arr, ref = DynamicArray(), []
    for i in range(100):  # проходим несколько границ роста ёмкости
        arr.append(i * i)
        ref.append(i * i)
        assert len(arr) == len(ref) <= arr.capacity
    assert [arr.get(i) for i in range(len(arr))] == ref
    arr.set(0, -1)
    assert arr.get(0) == -1
    try:
        arr.get(len(arr))
        assert False, "ожидался IndexError"
    except IndexError:
        pass

    # --- Stack: порядок LIFO, сверка с list ---
    st, ref = Stack(), []
    for x in [1, 2, 3]:
        st.push(x)
        ref.append(x)
    assert st.peek() == ref[-1]
    while ref:
        assert st.pop() == ref.pop()
    assert len(st) == 0

    # --- Deque: порядок FIFO и работа с обоих концов, сверка с collections.deque ---
    dq, ref = Deque(), collections.deque()
    dq.push_back(1), ref.append(1)
    dq.push_front(0), ref.appendleft(0)
    dq.push_back(2), ref.append(2)
    assert dq.pop_front() == ref.popleft() == 0
    assert dq.pop_back() == ref.pop() == 2
    assert dq.pop_front() == ref.popleft() == 1
    assert len(dq) == len(ref) == 0
    try:
        dq.pop_front()
        assert False, "ожидался IndexError"
    except IndexError:
        pass
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 5. Замеры (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5


def bench(fn, *args) -> float:
    """Медиана времени выполнения fn(*args) по REPEATS запускам, с прогревом."""
    fn(*args)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def appends_dynamic_array(n: int) -> None:
    """n последовательных append в свой DynamicArray."""
    arr = DynamicArray()
    for i in range(n):
        arr.append(i)


def inserts_front_list(n: int) -> None:
    """n вставок в начало встроенного list — ожидаемо O(n) на операцию."""
    a: list[int] = []
    for i in range(n):
        a.insert(0, i)


def inserts_front_deque(n: int) -> None:
    """n вставок в начало collections.deque — ожидаемо O(1) на операцию."""
    d: collections.deque = collections.deque()
    for i in range(n):
        d.appendleft(i)


def run_benchmarks(seed: int) -> None:
    """Средняя стоимость append и сравнение вставки в начало list/deque."""
    rng = random.Random(seed)
    _ = rng.random()  # данные варианта фиксируются seed (см. reproducibility.md)
    print("\nСредняя стоимость append (DynamicArray), демонстрация амортизированной O(1):")
    for n in SIZES:
        t = bench(appends_dynamic_array, n)
        print(f"  n={n:>7}  всего t={t:.6f} c  на операцию t/n={t / n:.3e} c")
    print("\nВставка в начало: list.insert(0, x) против deque.appendleft:")
    for n in SIZES:
        if n > 30_000:
            continue  # вставка в начало list квадратична по суммарному времени
        t_list = bench(inserts_front_list, n)
        t_deque = bench(inserts_front_deque, n)
        print(f"  n={n:>7}  list={t_list:.6f} c  deque={t_deque:.6f} c")
    # TODO: снять аналогичные замеры для push_front своего Deque;
    # TODO: построить график t/n от n для append и включить его в отчёт;
    # TODO: провести амортизированный анализ push_back методом учёта (в отчёте).


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
