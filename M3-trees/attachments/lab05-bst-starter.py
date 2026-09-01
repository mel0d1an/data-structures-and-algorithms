#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 5. Бинарное дерево поиска: обходы, вставка и удаление — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-05 и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST понадобится повторно в ДЗ 2
(Cases/kim-02-bst-height-experiment.md) — держите его чистым и переносимым.

Запуск: python lab05-bst-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
from collections import deque

# ---------------------------------------------------------------------------
# 1. Бинарное дерево поиска (реализуется вручную, без сторонних библиотек)
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    """Бинарное дерево поиска без дубликатов ключей.

    Инвариант: для каждого узла все ключи левого поддерева меньше key,
    все ключи правого — больше. Ожидаемая сложность операций: TODO
    (выразить через высоту h и обосновать в отчёте).
    """

    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Вставка ключа; повторная вставка существующего ключа игнорируется."""
        # TODO: спуск от корня до свободной позиции с сохранением инварианта
        raise NotImplementedError

    def search(self, key: int) -> bool:
        """Возвращает True, если ключ есть в дереве."""
        # TODO: спуск от корня со сравнением ключей
        raise NotImplementedError

    def delete(self, key: int) -> None:
        """Удаление ключа. Обработать три случая:

        1) лист — просто отцепить от родителя;
        2) один ребёнок — заменить узел его ребёнком;
        3) два ребёнка — заменить ключ преемником (минимум правого
           поддерева) и удалить преемника из правого поддерева.
        Отсутствующий ключ игнорируется.
        """
        # TODO: реализовать все три случая
        raise NotImplementedError

    # -- Обходы --------------------------------------------------------------

    def in_order(self) -> list[int]:
        """Симметричный обход (лево — узел — право): рекурсивно."""
        # TODO: для корректного BST результат — возрастающая последовательность
        raise NotImplementedError

    def pre_order(self) -> list[int]:
        """Прямой обход (узел — лево — право): рекурсивно."""
        # TODO
        raise NotImplementedError

    def post_order(self) -> list[int]:
        """Обратный обход (лево — право — узел): рекурсивно."""
        # TODO
        raise NotImplementedError

    def level_order(self) -> list[int]:
        """Обход в ширину по уровням: итеративно через очередь (deque)."""
        # TODO: использовать collections.deque, без рекурсии
        raise NotImplementedError

    # -- Характеристики дерева ----------------------------------------------

    def height(self) -> int:
        """Высота дерева: число рёбер на самом длинном пути от корня.

        Пустое дерево имеет высоту -1, дерево из одного узла — 0.
        """
        # TODO
        raise NotImplementedError

    def size(self) -> int:
        """Число узлов в дереве."""
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Верификация: инвариант BST и сверка с эталоном (docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные случаи + сверка операций с эталоном set/sorted."""
    # Пустое дерево
    t = BST()
    assert t.search(1) is False
    assert t.in_order() == []
    assert t.height() == -1 and t.size() == 0
    t.delete(1)  # удаление из пустого дерева не должно падать

    # Один узел
    t.insert(5)
    assert t.search(5) and not t.search(4)
    assert t.height() == 0 and t.size() == 1

    # Три случая удаления на маленьком дереве: 5, 2, 8, 1, 3
    for k in (2, 8, 1, 3):
        t.insert(k)
    t.delete(1)                       # лист
    assert t.in_order() == [2, 3, 5, 8]
    t.delete(2)                       # узел с одним ребёнком
    assert t.in_order() == [3, 5, 8]
    t.delete(5)                       # корень с двумя детьми (через преемника)
    assert t.in_order() == [3, 8]

    # Обходы на известном дереве 4-2-6-1-3-5-7 (вставка по уровням)
    t2 = BST()
    for k in (4, 2, 6, 1, 3, 5, 7):
        t2.insert(k)
    assert t2.in_order() == [1, 2, 3, 4, 5, 6, 7]
    assert t2.pre_order() == [4, 2, 1, 3, 6, 5, 7]
    assert t2.post_order() == [1, 3, 2, 5, 7, 6, 4]
    assert t2.level_order() == [4, 2, 6, 1, 3, 5, 7]
    assert t2.height() == 2 and t2.size() == 7

    # Случайные последовательности команд: сверка с эталоном из stdlib
    rng = random.Random(0)
    for _ in range(100):
        t3 = BST()
        etalon: set[int] = set()
        for _ in range(rng.randint(1, 80)):
            k = rng.randint(-30, 30)
            if rng.random() < 0.6:
                t3.insert(k)
                etalon.add(k)
            else:
                t3.delete(k)
                etalon.discard(k)
            # Инвариант BST: in-order даёт отсортированную последовательность
            assert t3.in_order() == sorted(etalon)
        for k in range(-30, 31):
            assert t3.search(k) == (k in etalon)
        assert t3.size() == len(etalon)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк: поиск в BST против поиска в списке (docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
QUERIES = 1_000  # число поисков на один замер


def bench(fn) -> float:
    """Медиана времени выполнения fn() по REPEATS запускам, с прогревом."""
    fn()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Сравнение времени QUERIES поисков в BST и в списке (оператор in)."""
    rng = random.Random(seed)
    print(f"{'n':>8} {'h(BST)':>7} {'t_bst, c':>10} {'t_list, c':>10}")
    for n in SIZES:
        keys = rng.sample(range(10 * n), n)   # случайные ключи без повторов
        queries = [rng.randint(0, 10 * n) for _ in range(QUERIES)]
        tree = BST()
        for k in keys:
            tree.insert(k)

        def search_bst() -> None:
            for q in queries:
                tree.search(q)

        def search_list() -> None:
            for q in queries:
                q in keys  # линейный поиск для сравнения

        print(f"{n:>8} {tree.height():>7} "
              f"{bench(search_bst):>10.6f} {bench(search_list):>10.6f}")
    # TODO: оформить результаты таблицей/графиком в отчёте;
    # TODO: сопоставить рост t_bst с высотой дерева, а t_list — с n;
    # TODO: в отчёте объяснить деградацию BST на упорядоченных ключах
    #       и гарантию высоты AVL-дерева (не более 1,44*log2(n)) — мостик к ДЗ 2.


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant  # seed по варианту — см. docs/reproducibility.md
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
