#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 1. Анализ временной сложности элементарных алгоритмов — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-01 и правилами использования генеративного ИИ
(docs/ai-verification.md). Каркас загрузки данных, замеров и построения
графиков уже готов — учебная задача в алгоритмах и в объяснении результатов.

Работа выполняется на данных СВОЕГО варианта. Перед первым запуском их нужно
сгенерировать (из корня репозитория курса):

    python scripts/generate_data.py --variant N --only arrays

Запуск (N — ваш номер варианта):

    python lab01-complexity-starter.py --variant N

Если заготовка скопирована в личный репозиторий и каталог с данными не находится
автоматически, укажите его явно:

    python lab01-complexity-starter.py --variant N --data ~/data-structures-and-algorithms/data/generated
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Параметры эксперимента
# ---------------------------------------------------------------------------

#: Размеры массивов, для которых generate_data.py создаёт файлы.
SIZES = (1_000, 3_000, 10_000, 30_000, 100_000)

#: Для квадратичного алгоритма n = 100 000 исключён: это порядка 15 минут.
#: Размер 500 берётся как префикс файла на 1 000 элементов — так у нас
#: остаётся пять точек, как требует задание.
QUADRATIC_SIZES = (500, 1_000, 3_000, 10_000, 30_000)

#: Показатели степени для замера бинарного возведения в степень.
EXPONENTS = (10**3, 10**4, 10**5, 10**6, 10**7)

#: Модуль для возведения в степень. Без него Python считает длинную арифметику,
#: и замер покажет рост длины чисел, а не число итераций (см. отчёт).
POW_MOD = 1_000_000_007
POW_BASE = 3

REPEATS = 5           # повторов на точку (берётся медиана)
POW_CALLS = 20_000    # вызовов binary_pow на один замер: иначе время неизмеримо мало

# ---------------------------------------------------------------------------
# 1. Алгоритмы (реализуются вручную, без sum/max и встроенного pow)
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


def binary_pow(x: int, n: int, mod: int | None = None) -> int:
    """Бинарное возведение в степень, n >= 0. Ожидаемая сложность: TODO.

    При заданном mod все умножения выполняются по модулю (результат x**n % mod).
    """
    # TODO: реализовать через квадрирование; при mod применять % mod после
    # каждого умножения
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Данные варианта: поиск каталога и загрузка
# ---------------------------------------------------------------------------


def find_data_dir(explicit: Path | None) -> Path:
    """Каталог с данными варианта: --data, либо data/generated рядом с работой."""
    if explicit is not None:
        if not explicit.is_dir():
            raise SystemExit(f"Каталог не найден: {explicit}")
        return explicit
    candidates = []
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        for parent in (base, *base.parents):
            candidates.append(parent / "data" / "generated")
    for path in candidates:
        if path.is_dir():
            return path
    raise SystemExit(
        "Не найден каталог data/generated с данными варианта.\n"
        "Сгенерируйте данные из корня репозитория курса:\n"
        "    python scripts/generate_data.py --variant N --only arrays\n"
        "или укажите каталог явно: --data <путь>")


def check_variant(data_dir: Path, variant: int) -> None:
    """Сверить номер варианта с паспортом данных (manifest.json)."""
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.is_file():
        print(f"ВНИМАНИЕ: в {data_dir} нет manifest.json — "
              f"не могу проверить, что данные относятся к варианту {variant}.")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = manifest.get("variant")
    if actual != variant:
        raise SystemExit(
            f"Данные в {data_dir} сгенерированы для варианта {actual}, "
            f"а работа запущена с --variant {variant}.\n"
            f"Перегенерируйте данные: "
            f"python scripts/generate_data.py --variant {variant} --only arrays")
    print(f"Данные варианта {variant} (seed={manifest.get('seed')}) из {data_dir}")


def load_array(data_dir: Path, kind: str, n: int, limit: int | None = None) -> list[int]:
    """Загрузить массив arrays_<kind>_<n>.txt; limit — взять только первые limit чисел."""
    path = data_dir / f"arrays_{kind}_{n}.txt"
    if not path.is_file():
        raise SystemExit(
            f"Не найден файл данных: {path}\n"
            f"Сгенерируйте его: python scripts/generate_data.py "
            f"--variant <ваш вариант> --only arrays")
    values = [int(line) for line in path.read_text(encoding="utf-8").split()]
    return values[:limit] if limit is not None else values


# ---------------------------------------------------------------------------
# 3. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные и типовые случаи + сверка с эталоном (sum, max, pow)."""
    # Граничные случаи
    assert array_sum([]) == 0
    assert array_sum([7]) == 7
    assert array_max([3, 1, 2]) == 3
    assert count_equal_pairs([]) == 0
    assert count_equal_pairs([5, 5, 5]) == 3          # пары (0,1), (0,2), (1,2)
    assert binary_pow(2, 0) == 1
    assert binary_pow(2, 10) == 1024
    assert binary_pow(2, 10, mod=1000) == 24

    # Сверка с эталонными реализациями на случайных данных
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(-50, 50) for _ in range(rng.randint(1, 60))]
        assert array_sum(a) == sum(a)
        assert array_max(a) == max(a)
    for _ in range(200):
        x, n = rng.randint(2, 50), rng.randint(0, 64)
        assert binary_pow(x, n, mod=POW_MOD) == pow(x, n, POW_MOD)

    # TODO: добавить собственные проверки инвариантов и описать их в отчёте
    # (например: count_equal_pairs на массиве из попарно различных элементов = 0).
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------


def bench(call) -> float:
    """Медиана времени выполнения call() по REPEATS запускам, с прогревом."""
    call()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        call()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def log_log_slope(points: list[tuple[int, float]]) -> float:
    """Наклон прямой в осях (log n, log t) — оценка показателя степени."""
    xs = [math.log10(n) for n, _ in points]
    ys = [math.log10(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            / sum((x - mx) ** 2 for x in xs))


def run_benchmarks(data_dir: Path) -> dict[str, list[tuple[int, float]]]:
    """Замеры на данных варианта. Возвращает {имя алгоритма: [(n, t), ...]}."""
    results: dict[str, list[tuple[int, float]]] = {}

    # Линейные алгоритмы — на случайных массивах всех размеров
    random_arrays = {n: load_array(data_dir, "random", n) for n in SIZES}
    for name, fn in (("array_sum", array_sum), ("array_max", array_max)):
        points = []
        print(f"\n{name}:")
        for n in SIZES:
            a = random_arrays[n]
            t = bench(lambda: fn(a))
            points.append((n, t))
            print(f"  n={n:>7}  t={t:.6f} c")
        results[name] = points

    # Квадратичный алгоритм — на массивах с дубликатами (иначе пар почти нет)
    print("\ncount_equal_pairs:")
    points = []
    for n in QUADRATIC_SIZES:
        file_n = n if n in SIZES else min(s for s in SIZES if s >= n)
        a = load_array(data_dir, "dups", file_n, limit=n)
        t = bench(lambda: count_equal_pairs(a))
        points.append((n, t))
        print(f"  n={n:>7}  t={t:.6f} c")
    results["count_equal_pairs"] = points

    # Логарифмический алгоритм: одна операция слишком быстра, замеряем пачку
    # вызовов и делим на их число. Считаем по модулю — см. POW_MOD.
    print(f"\nbinary_pow (по {POW_CALLS} вызовов на точку, по модулю {POW_MOD}):")
    points = []
    for e in EXPONENTS:
        def batch(e: int = e) -> None:
            for _ in range(POW_CALLS):
                binary_pow(POW_BASE, e, mod=POW_MOD)
        t = bench(batch) / POW_CALLS
        points.append((e, t))
        print(f"  n={e:>9}  log2(n)={math.log2(e):5.1f}  t={t:.9f} c")
    results["binary_pow"] = points

    return results


# ---------------------------------------------------------------------------
# 5. Графики
# ---------------------------------------------------------------------------


def plot_results(results: dict[str, list[tuple[int, float]]], out_dir: Path) -> None:
    """Два графика: log-log для степенных алгоритмов и t(log n) для бинарной степени."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # сохранение в файл без графической оболочки
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib не установлен — графики пропущены "
              "(pip install -r requirements.txt)")
        return

    power_law = ("array_sum", "array_max", "count_equal_pairs")
    fig, ax = plt.subplots(figsize=(7, 5))
    for name in power_law:
        points = results[name]
        ns = [n for n, _ in points]
        ts = [t for _, t in points]
        ax.plot(ns, ts, marker="o", label=f"{name} (наклон ≈ {log_log_slope(points):.2f})")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("размер входа n")
    ax.set_ylabel("время, с")
    ax.set_title("Время работы в осях log-log")
    ax.grid(True, which="both", linewidth=0.3)
    ax.legend()
    fig.tight_layout()
    loglog_path = out_dir / "lab01_loglog.png"
    fig.savefig(loglog_path, dpi=150)

    points = results["binary_pow"]
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    ax2.plot([math.log2(n) for n, _ in points], [t for _, t in points], marker="o")
    ax2.set_xlabel("log₂ n (число бит показателя)")
    ax2.set_ylabel("время одного вызова, с")
    ax2.set_title("Бинарное возведение в степень: t(log₂ n)")
    ax2.grid(True, linewidth=0.3)
    fig2.tight_layout()
    pow_path = out_dir / "lab01_binary_pow.png"
    fig2.savefig(pow_path, dpi=150)

    print(f"\nГрафики сохранены:\n  {loglog_path}\n  {pow_path}")
    # TODO: в отчёте объяснить, почему для binary_pow выбраны ЛИНЕЙНЫЕ оси
    # по log₂ n, а не log-log (какой вид имеет логарифмическая зависимость
    # в осях log-log и почему по ней трудно судить о порядке роста).


# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--data", type=Path, default=None,
                    help="каталог с данными варианта (по умолчанию ищется data/generated)")
    ap.add_argument("--out", type=Path, default=Path.cwd(),
                    help="каталог для графиков (по умолчанию текущий)")
    args = ap.parse_args()

    data_dir = find_data_dir(args.data)
    check_variant(data_dir, args.variant)

    self_check()
    results = run_benchmarks(data_dir)

    print("\nНаклон в осях log-log (оценка показателя степени):")
    for name in ("array_sum", "array_max", "count_equal_pairs"):
        print(f"  {name:20s} {log_log_slope(results[name]):.3f}")
    # TODO: сопоставить наклоны с аналитическими оценками из отчёта
    # и объяснить расхождения (константы, кэш, накладные расходы интерпретатора).

    plot_results(results, args.out)


if __name__ == "__main__":
    main()
