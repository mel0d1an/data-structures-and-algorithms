
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией."""

from __future__ import annotations

import argparse
import csv
import math
import platform
import random
import statistics
import sys
import time
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком с досрочным выходом. O(n) / O(n²)."""

    result = list(a)
    comparisons = 0
    swaps = 0

    for end in range(len(result) - 1, 0, -1):
        swapped = False

        for j in range(end):
            comparisons += 1

            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swaps += 1
                swapped = True

        if not swapped:
            break

    return result, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Лучший случай O(n), худший O(n²)."""

    result = list(a)
    comparisons = 0
    moves = 0

    for i in range(1, len(result)):
        current = result[i]
        j = i - 1

        while j >= 0:
            comparisons += 1

            if result[j] > current:
                result[j + 1] = result[j]
                moves += 1
                j -= 1
            else:
                break

        result[j + 1] = current

    return result, comparisons, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Всегда Θ(n²) сравнений."""

    result = list(a)
    comparisons = 0
    swaps = 0

    for i in range(len(result) - 1):
        min_index = i

        for j in range(i + 1, len(result)):
            comparisons += 1

            if result[j] < result[min_index]:
                min_index = j

        if min_index != i:
            result[i], result[min_index] = result[min_index], result[i]
            swaps += 1

    return result, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным pivot
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с рандомизированным pivot и трёхчастным разбиением.

    Средняя ожидаемая сложность O(n log n).
    Худшая сложность O(n²).
    Используется явный стек вместо рекурсии.
    """

    result = list(a)

    if rng is None:
        rng = random.Random()

    if len(result) < 2:
        return result

    # Границы подмассивов: [lo, hi).
    stack = [(0, len(result))]

    while stack:
        lo, hi = stack.pop()

        while hi - lo > 1:

            # Случайный опорный элемент.
            pivot = result[rng.randrange(lo, hi)]

            # Трёхчастное разбиение:
            # [lo, lt)     — элементы меньше pivot
            # [lt, i)      — элементы равны pivot
            # (gt, hi)     — элементы больше pivot

            lt = lo
            i = lo
            gt = hi - 1

            while i <= gt:

                if result[i] < pivot:
                    result[lt], result[i] = result[i], result[lt]
                    lt += 1
                    i += 1

                elif result[i] > pivot:
                    result[i], result[gt] = result[gt], result[i]
                    gt -= 1

                else:
                    i += 1

            left = (lo, lt)
            right = (gt + 1, hi)

            left_size = left[1] - left[0]
            right_size = right[1] - right[0]

            # Обрабатываем меньшую часть сразу,
            # большую помещаем в стек.
            if left_size < right_size:

                if right_size > 1:
                    stack.append(right)

                lo, hi = left

            else:

                if left_size > 1:
                    stack.append(left)

                lo, hi = right

    return result


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности
# ---------------------------------------------------------------------------


class _KeyOnly:
    """Объект, сравниваемый только по ключу пары (ключ, метка)."""

    def __init__(self, pair: tuple) -> None:
        self.pair = pair
        self.key = pair[0]

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key

    def __repr__(self):
        return repr(self.pair)


def stability_results(seed: int = 31) -> list[dict]:

    sample = [
        (2, "a"),
        (1, "b"),
        (2, "c"),
        (1, "d"),
    ]

    original_order = {}

    for key, label in sample:
        original_order.setdefault(key, []).append(label)

    algorithms = {
        "bubble_sort": lambda a: bubble_sort(a)[0],

        "insertion_sort": lambda a: insertion_sort(a)[0],

        "selection_sort": lambda a: selection_sort(a)[0],

        "quick_sort": lambda a: quick_sort(a, random.Random(seed)),
    }

    results = []

    for name, sort_fn in algorithms.items():

        wrapped = [_KeyOnly(pair) for pair in sample]

        sorted_items = sort_fn(wrapped)

        sorted_pairs = [item.pair for item in sorted_items]

        actual_order = {}

        for key, label in sorted_pairs:
            actual_order.setdefault(key, []).append(label)

        stable = all(
            actual_order.get(key) == labels
            for key, labels in original_order.items()
        )

        results.append({
            "algorithm": name,
            "result": sorted_pairs,
            "stable": stable,
        })

    return results


def stability_demo() -> list[dict]:
    """Показывает стабильность четырёх сортировок."""

    results = stability_results()

    print("\nДемонстрация стабильности:")
    print("Исходный массив: [(2, 'a'), (1, 'b'), (2, 'c'), (1, 'd')]")

    for row in results:

        status = "стабильная" if row["stable"] else "нестабильная"

        print(
            f"  {row['algorithm']:<16} "
            f"{row['result']} — {status}"
        )

    return results


# ---------------------------------------------------------------------------
# 4. Генерация данных
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:

    rng = random.Random(seed + n)

    data = [
        rng.randint(-1_000_000, 1_000_000)
        for _ in range(n)
    ]

    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация
# ---------------------------------------------------------------------------


ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],

    "insertion_sort": lambda a: insertion_sort(a)[0],

    "selection_sort": lambda a: selection_sort(a)[0],

    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


COUNTER_ALGORITHMS = {
    "bubble_sort": bubble_sort,
    "insertion_sort": insertion_sort,
    "selection_sort": selection_sort,
}


def is_sorted(a: list) -> bool:

    return all(
        a[i] <= a[i + 1]
        for i in range(len(a) - 1)
    )


class SelfCheckError(Exception):
    pass


def expect(condition: bool, message: str) -> None:

    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    """Проверяет инварианты и сравнивает с sorted()."""

    boundary = [
        [],
        [7],
        [5, 5, 5, 5],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, -1, 0, -1, 8, 3],
        [2, 1],
    ]

    for original in boundary:

        data = list(original)

        result = fn(data)

        expect(
            isinstance(result, list),
            "Результат должен быть списком"
        )

        expect(
            data == original,
            "Исходный массив не должен изменяться"
        )

        expect(
            result is not data,
            "Должна возвращаться новая копия"
        )

        expect(
            is_sorted(result),
            f"Массив не отсортирован: {result}"
        )

        expect(
            sorted(result) == sorted(original),
            "Результат не является перестановкой входа"
        )

    # 300 случайных тестов.

    rng = random.Random(0)

    for test_no in range(300):

        original = [
            rng.randint(-100, 100)
            for _ in range(rng.randint(0, 80))
        ]

        data = list(original)

        result = fn(data)

        expect(
            result == sorted(original),
            f"Ошибка на случайном тесте {test_no}"
        )

        expect(
            data == original,
            "Исходный массив был изменён"
        )


def check_counters() -> None:
    """Проверка счётчиков сравнений и перемещений."""

    # Bubble Sort: упорядоченный массив.

    _, comparisons, swaps = bubble_sort([1, 2, 3, 4])

    expect(
        comparisons == 3 and swaps == 0,
        "Ошибка счётчиков Bubble Sort на упорядоченном массиве"
    )

    # Bubble Sort: обратный порядок.

    _, comparisons, swaps = bubble_sort([4, 3, 2, 1])

    expect(
        comparisons == 6 and swaps == 6,
        "Ошибка счётчиков Bubble Sort на обратном массиве"
    )

    # Insertion Sort: упорядоченный массив.

    _, comparisons, moves = insertion_sort([1, 2, 3, 4])

    expect(
        comparisons == 3 and moves == 0,
        "Ошибка счётчиков Insertion Sort на упорядоченном массиве"
    )

    # Insertion Sort: обратный порядок.

    _, comparisons, moves = insertion_sort([4, 3, 2, 1])

    expect(
        comparisons == 6 and moves == 6,
        "Ошибка счётчиков Insertion Sort на обратном массиве"
    )

    # Selection Sort: фиксированное число сравнений.

    for n in range(9):

        data = list(range(n))

        _, comparisons, _ = selection_sort(data)

        expected = n * (n - 1) // 2

        expect(
            comparisons == expected,
            f"Selection Sort: ожидалось {expected}, получено {comparisons}"
        )


def check_stability() -> None:

    results = {
        row["algorithm"]: row["stable"]
        for row in stability_results()
    }

    expect(
        results["bubble_sort"],
        "Bubble Sort должна быть стабильной"
    )

    expect(
        results["insertion_sort"],
        "Insertion Sort должна быть стабильной"
    )

    expect(
        not results["selection_sort"],
        "Selection Sort должна быть нестабильной"
    )

    expect(
        not results["quick_sort"],
        "QuickSort должна быть нестабильной на демонстрационном массиве"
    )


def self_check() -> None:

    checks = [
        (name, lambda fn=fn: check_algorithm(fn))
        for name, fn in ALGORITHMS.items()
    ]

    checks.append(("счётчики", check_counters))
    checks.append(("стабильность", check_stability))

    failed = 0

    print("self_check:")

    for name, check in checks:

        try:
            check()

        except NotImplementedError as err:

            where = traceback.extract_tb(err.__traceback__)[-1].name

            print(f"  {name}: не реализовано — {where}")

            failed += 1

        except SelfCheckError as err:

            print(f"  {name}: ОШИБКА — {err}")

            failed += 1

        except Exception:

            print(f"  {name}: ИСКЛЮЧЕНИЕ")

            traceback.print_exc(file=sys.stdout)

            failed += 1

        else:

            print(f"  {name}: OK")

    if failed:

        raise SystemExit(
            f"self_check: не пройдено разделов — {failed}; "
            "замеры не выполняются."
        )

    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк
# ---------------------------------------------------------------------------


SIZES_QUADRATIC = [
    500,
    1_000,
    2_000,
    4_000,
    8_000,
]

SIZES_QUICK = [
    1_000,
    3_000,
    10_000,
    30_000,
    100_000,
]

REPEATS = 5


def bench(fn, data: list) -> float:
    """Прогрев + пять измерений + медиана."""

    fn(list(data))

    times = []

    for _ in range(REPEATS):

        arg = list(data)

        t0 = time.perf_counter()

        fn(arg)

        times.append(time.perf_counter() - t0)

    return statistics.median(times)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        writer.writerows(rows)


def calculate_slope(rows: list[dict]) -> float:
    """Наклон линии в координатах log-log."""

    xs = [math.log(row["n"]) for row in rows]

    ys = [
        math.log(row["median_seconds"])
        for row in rows
    ]

    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(ys)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(xs, ys)
    )

    denominator = sum(
        (x - mean_x) ** 2
        for x in xs
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


def plot_results(rows: list[dict], out_dir: Path) -> None:
    """Создаёт отдельный log-log график для каждого алгоритма."""

    input_classes = [
        "упорядоченный",
        "случайный",
        "обратный",
    ]

    for algorithm in ALGORITHMS:

        fig, ax = plt.subplots(figsize=(9, 6))

        for input_class in input_classes:

            group = [
                row for row in rows
                if row["algorithm"] == algorithm
                and row["input_class"] == input_class
            ]

            group.sort(key=lambda row: row["n"])

            ax.loglog(
                [row["n"] for row in group],
                [row["median_seconds"] for row in group],
                marker="o",
                linewidth=2,
                label=input_class,
            )

        ax.set_title(f"{algorithm}: log-log")

        ax.set_xlabel("Размер массива n")

        ax.set_ylabel("Медианное время, секунды")

        ax.grid(True, which="both", linestyle="--", alpha=0.4)

        ax.legend()

        fig.tight_layout()

        filename = f"lab03_{algorithm}_loglog.png"

        fig.savefig(
            out_dir / filename,
            dpi=180
        )

        plt.close(fig)


def run_benchmarks(seed: int) -> None:
    """Измерения времени, счётчиков и построение графиков."""

    module_dir = Path(__file__).resolve().parent.parent

    out_dir = module_dir / "lab03-results"

    out_dir.mkdir(parents=True, exist_ok=True)

    timing_rows = []

    counter_rows = []

    # Один воспроизводимый поток случайных pivot для всей серии.

    pivot_rng = random.Random(seed)

    plans = [
        (
            "bubble_sort",
            ALGORITHMS["bubble_sort"],
            bubble_sort,
            SIZES_QUADRATIC,
        ),
        (
            "insertion_sort",
            ALGORITHMS["insertion_sort"],
            insertion_sort,
            SIZES_QUADRATIC,
        ),
        (
            "selection_sort",
            ALGORITHMS["selection_sort"],
            selection_sort,
            SIZES_QUADRATIC,
        ),
        (
            "quick_sort",
            lambda a: quick_sort(a, pivot_rng),
            None,
            SIZES_QUICK,
        ),
    ]

    print("\nНачало экспериментальных замеров.")

    print(f"Seed: {seed}")

    print(f"Количество повторов: {REPEATS}")

    for name, fn, counter_fn, sizes in plans:

        print(f"\n{name}:")

        for n in sizes:

            inputs = make_inputs(n, seed)

            for input_class, data in inputs.items():

                # Замер времени.

                median_time = bench(fn, data)

                timing_rows.append({
                    "algorithm": name,
                    "n": n,
                    "input_class": input_class,
                    "median_seconds": median_time,
                })

                # Счётчики простых сортировок.

                counter_text = ""

                if counter_fn is not None:

                    _, comparisons, moves = counter_fn(data)

                    counter_rows.append({
                        "algorithm": name,
                        "n": n,
                        "input_class": input_class,
                        "comparisons": comparisons,
                        "moves": moves,
                    })

                    counter_text = (
                        f" | сравнений={comparisons}"
                        f" | обменов/сдвигов={moves}"
                    )

                print(
                    f"  n={n:>7} "
                    f"| {input_class:<13} "
                    f"| медиана={median_time:.6f} с"
                    f"{counter_text}"
                )

    # Сохранение таблиц.

    write_csv(
        out_dir / "lab03_timings.csv",
        timing_rows,
        [
            "algorithm",
            "n",
            "input_class",
            "median_seconds",
        ],
    )

    write_csv(
        out_dir / "lab03_counters.csv",
        counter_rows,
        [
            "algorithm",
            "n",
            "input_class",
            "comparisons",
            "moves",
        ],
    )

    # Построение графиков.

    plot_results(timing_rows, out_dir)

    # Вычисление наклонов log-log.

    print("\nНаклоны log-log:")

    for algorithm in ALGORITHMS:

        for input_class in (
            "упорядоченный",
            "случайный",
            "обратный",
        ):

            group = [
                row for row in timing_rows
                if row["algorithm"] == algorithm
                and row["input_class"] == input_class
            ]

            group.sort(key=lambda row: row["n"])

            value = calculate_slope(group)

            print(
                f"  {algorithm:<16} "
                f"{input_class:<13} "
                f"наклон={value:.3f}"
            )

    print("\nЭксперименты завершены.")

    print(f"\nРезультаты сохранены в: {out_dir}")

    print("\nСозданы файлы:")

    print("  lab03_timings.csv")
    print("  lab03_counters.csv")

    for algorithm in ALGORITHMS:
        print(f"  lab03_{algorithm}_loglog.png")

    print("\nCPU:", platform.processor())

    print("Python:", platform.python_version())


# ---------------------------------------------------------------------------
# 7. Точка входа
# ---------------------------------------------------------------------------


def main() -> None:

    ap = argparse.ArgumentParser(description=__doc__)

    ap.add_argument(
        "--variant",
        type=int,
        required=True,
        help="номер варианта",
    )

    ap.add_argument(
        "--check-only",
        action="store_true",
        help="только проверки, без длительных замеров",
    )

    args = ap.parse_args()

    if args.variant < 1:
        ap.error("номер варианта должен быть положительным")

    seed = 30 + args.variant

    random.seed(seed)

    print(f"Вариант: {args.variant}")

    print(f"Seed: {seed}")

    self_check()

    stability_demo()

    if args.check_only:

        print("\nПроверки завершены. Замеры пропущены.")

        return

    run_benchmarks(seed)


if __name__ == "__main__":
    main()
