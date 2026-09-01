#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 1. Анализ временной сложности элементарных алгоритмов — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-01 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab01-complexity-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Алгоритмы (реализуются вручную, без numpy/встроенных sum/max в основной части)
# ---------------------------------------------------------------------------


def array_sum(a: list[int]) -> int:
    """Сумма элементов массива. Ожидаемая сложность: TODO (обосновать в отчёте)."""
    # TODO: реализовать циклом
    raise NotImplementedError


def array_max(a: list[int]) -> int:
    """Максимум массива (массив непуст). Ожидаемая сложность: TODO."""
    # TODO: реализовать циклом
    raise NotImplementedError


def count_equal_pairs(a: list[int]) -> int:
    """Число пар (i, j), i < j, таких что a[i] == a[j]. Ожидаемая сложность: TODO."""
    # TODO: реализовать двойным циклом
    raise NotImplementedError


def binary_pow(x: float, n: int) -> float:
    """Бинарное возведение в степень, n >= 0. Ожидаемая сложность: TODO."""
    # TODO: реализовать через квадрирование
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные и типовые случаи + сверка с эталоном (sum, max, pow)."""
    assert array_sum([]) == 0
    assert array_sum([7]) == 7
    assert array_max([3, 1, 2]) == 3
    assert count_equal_pairs([]) == 0
    assert count_equal_pairs([5, 5, 5]) == 3
    assert binary_pow(2, 10) == 1024
    rng = random.Random(0)
    for _ in range(200):  # сравнение с эталонной реализацией
        a = [rng.randint(-50, 50) for _ in range(rng.randint(1, 60))]
        assert array_sum(a) == sum(a)
        assert array_max(a) == max(a)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5


def bench(fn, data: list[int]) -> float:
    """Медиана времени выполнения fn(data) по REPEATS запускам, с прогревом."""
    fn(data)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    datasets = {n: [rng.randint(-1000, 1000) for _ in range(n)] for n in SIZES}
    for name, fn in [("array_sum", array_sum), ("array_max", array_max),
                     ("count_equal_pairs", count_equal_pairs)]:
        print(f"\n{name}:")
        for n in SIZES:
            if name == "count_equal_pairs" and n > 30_000:
                continue  # квадратичный алгоритм: большие n занимают минуты
            print(f"  n={n:>7}  t={bench(fn, datasets[n]):.6f} c")
    # TODO: построить log-log графики (matplotlib) и включить их в отчёт;
    # TODO: сопоставить наклоны с аналитическими оценками, объяснить расхождения.


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
