#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 2. Эксперимент: высота BST и деградация операций — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-02 (Cases) и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST из ЛР 5 рекомендуется подключить как
модуль; ниже дан минимальный узел и сигнатуры на случай автономного запуска.

Запуск: python dz02-bst-height-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Узел и итеративная вставка
#    Внимание: на упорядоченном потоке дерево вырождается в список глубиной
#    до 10^4, поэтому вставка и обходы должны быть итеративными —
#    рекурсивные варианты вызовут RecursionError.
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


def insert_iter(root: Node | None, key: int) -> Node:
    """Итеративная вставка ключа в BST; возвращает корень дерева.

    Дубликаты игнорируются (ключи в эксперименте уникальны).
    """
    # TODO: спуститься от корня циклом до свободной позиции и подвесить узел
    raise NotImplementedError


def build_bst(keys: list[int]) -> Node | None:
    """Строит BST последовательной итеративной вставкой ключей."""
    root: Node | None = None
    for key in keys:
        root = insert_iter(root, key)
    return root


# ---------------------------------------------------------------------------
# 2. Измеряемые величины: высота и средняя глубина узла
# ---------------------------------------------------------------------------


def tree_height(root: Node | None) -> int:
    """Высота дерева: число рёбер на самом длинном пути от корня до листа.

    Пустое дерево: -1; один узел: 0. Реализовать итеративно
    (обход в ширину или в глубину с явным стеком/очередью).
    """
    # TODO: реализовать итеративный обход с отслеживанием глубины
    raise NotImplementedError


def sum_depths(root: Node | None) -> int:
    """Сумма глубин всех узлов (глубина корня — 0). Итеративно."""
    # TODO: обойти дерево, накапливая глубину каждого узла
    raise NotImplementedError


def count_nodes(root: Node | None) -> int:
    """Число узлов дерева. Итеративно."""
    # TODO: реализовать подсчёт узлов
    raise NotImplementedError


def avg_depth(root: Node | None) -> float:
    """Средняя глубина узла: sum_depths / count_nodes (0.0 для пустого)."""
    # TODO: выразить через sum_depths и count_nodes, обработать пустое дерево
    raise NotImplementedError


def inorder_keys(root: Node | None) -> list[int]:
    """Ключи in-order-обхода (итеративно, с явным стеком) — для верификации."""
    # TODO: реализовать итеративный in-order
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные деревья, аналитические значения, сверка с эталоном sorted()."""
    # Граничные случаи: пустое дерево и один узел
    assert tree_height(None) == -1
    assert avg_depth(None) == 0.0
    single = build_bst([42])
    assert tree_height(single) == 0
    assert count_nodes(single) == 1

    # Типовой случай: [2, 1, 3] — идеально сбалансированное дерево из 3 узлов
    small = build_bst([2, 1, 3])
    assert tree_height(small) == 1
    assert sum_depths(small) == 2  # 0 (корень) + 1 + 1

    # Вырожденный случай: упорядоченные ключи 1..n дают "список"
    n = 100
    degenerate = build_bst(list(range(1, n + 1)))
    assert tree_height(degenerate) == n - 1
    assert avg_depth(degenerate) == (n - 1) / 2  # (0+1+...+(n-1)) / n

    # Сверка с эталоном стандартной библиотеки: инвариант BST —
    # in-order-обход совпадает с sorted() на случайных наборах ключей
    rng = random.Random(0)
    for _ in range(200):
        keys = rng.sample(range(-1000, 1000), rng.randint(1, 60))
        root = build_bst(keys)
        assert inorder_keys(root) == sorted(keys)
        assert count_nodes(root) == len(keys)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент и каркас замеров (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [100, 300, 1_000, 3_000, 10_000]  # геометрический шаг, n до 10^4
REPEATS = 5


def random_keys(n: int, rng: random.Random) -> list[int]:
    """n уникальных случайных ключей (детерминированно по seed варианта)."""
    return rng.sample(range(10 * n), n)


def ordered_keys(n: int) -> list[int]:
    """n упорядоченных ключей 1..n — худший поток вставок для BST."""
    return list(range(1, n + 1))


def bench_search(root: Node | None, queries: list[int]) -> float:
    """Медиана времени поиска всех ключей queries по REPEATS запускам."""

    def run() -> None:
        for q in queries:
            node = root
            while node is not None and node.key != q:
                node = node.left if q < node.key else node.right

    run()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        run()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_experiment(seed: int) -> None:
    """Таблица: n, высота и средняя глубина для двух потоков, опорные величины."""
    rng = random.Random(seed)
    header = (f"{'n':>7} {'h_случ':>8} {'d_случ':>8} "
              f"{'h_упор':>8} {'d_упор':>8} {'log2(n)':>8}")
    print(header)
    import math
    for n in SIZES:
        root_rand = build_bst(random_keys(n, rng))
        root_ord = build_bst(ordered_keys(n))
        print(f"{n:>7} {tree_height(root_rand):>8} "
              f"{avg_depth(root_rand):>8.1f} {tree_height(root_ord):>8} "
              f"{avg_depth(root_ord):>8.1f} {math.log2(n):>8.1f}")
        # TODO: замерить bench_search для обоих деревьев на одинаковых
        #       запросах и включить сравнение времени в отчёт
    # TODO: построить графики h(n) для обоих потоков на фоне log2(n) и n
    #       (matplotlib) и включить их в отчёт
    # TODO: в отчёте объяснить деградацию операций до O(n), привести справку
    #       об AVL (высота <= 1.44*log2(n), цена балансировки) и
    #       вывод-рекомендацию о выборе структуры


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed)


if __name__ == "__main__":
    main()
