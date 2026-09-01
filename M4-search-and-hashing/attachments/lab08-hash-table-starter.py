#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 8. Хеш-таблица с отдельным цепочечным хешированием — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-08 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab08-hash-table-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import string
import time

# ---------------------------------------------------------------------------
# 1. Хеш-функции для строковых ключей
# ---------------------------------------------------------------------------

P = 31  # основание полинома (простое число, близкое к размеру алфавита)


def poly_hash(key: str, mod: int) -> int:
    """Полиномиальный хеш строки по модулю mod.

    h(s) = (s[0]·P^(k-1) + s[1]·P^(k-2) + … + s[k-1]) mod mod,
    где s[i] — код символа (ord). Ожидаемое свойство: равномерное
    распределение ключей по бакетам (обосновать в отчёте).
    """
    # TODO: реализовать по схеме Горнера, беря остаток на каждом шаге
    raise NotImplementedError


def bad_hash(key: str, mod: int) -> int:
    """Заведомо плохая хеш-функция: только первый символ ключа.

    Все ключи с общим первым символом попадают в один бакет — используется
    в эксперименте с гистограммой длин цепочек как контрпример.
    """
    return (ord(key[0]) if key else 0) % mod


# ---------------------------------------------------------------------------
# 2. Хеш-таблица с отдельными цепочками
# ---------------------------------------------------------------------------


class HashTable:
    """Хеш-таблица: бакеты — списки пар (ключ, значение) (отдельные цепочки).

    Инварианты (проверяются в check_invariants):
      1) каждая пара лежит в бакете с индексом hash_fn(ключ, число бакетов);
      2) сумма длин всех цепочек равна len(таблицы);
      3) ключи внутри таблицы не повторяются.
    """

    INITIAL_CAPACITY = 8

    def __init__(self, capacity: int = INITIAL_CAPACITY, hash_fn=poly_hash,
                 max_load_factor: float = 0.75) -> None:
        self._buckets: list[list[tuple[str, object]]] = [[] for _ in range(capacity)]
        self._size = 0
        self._hash_fn = hash_fn
        # max_load_factor=float("inf") отключает rehash — нужно в эксперименте,
        # где коэффициент загрузки задаётся вручную
        self._max_load_factor = max_load_factor

    def _bucket_index(self, key: str) -> int:
        """Индекс бакета для ключа при текущем числе бакетов."""
        return self._hash_fn(key, len(self._buckets))

    @property
    def load_factor(self) -> float:
        """Коэффициент загрузки α = размер / число бакетов."""
        return self._size / len(self._buckets)

    def put(self, key: str, value: object) -> None:
        """Вставить пару или обновить значение существующего ключа.

        После вставки нового ключа при load_factor > max_load_factor
        вызвать _rehash(). Средняя сложность: TODO (обосновать в отчёте).
        """
        # TODO: найти ключ в своей цепочке; обновить либо добавить пару,
        # TODO: увеличить _size и при необходимости выполнить _rehash()
        raise NotImplementedError

    def get(self, key: str, default: object = None) -> object:
        """Вернуть значение по ключу или default, если ключа нет."""
        # TODO: просмотреть цепочку бакета ключа
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """Удалить ключ; если ключа нет — возбудить KeyError."""
        # TODO: удалить пару из цепочки, уменьшить _size
        raise NotImplementedError

    def __len__(self) -> int:
        return self._size

    def _rehash(self) -> None:
        """Удвоить число бакетов и заново распределить все пары."""
        # TODO: создать новые бакеты и переложить пары по новым индексам
        raise NotImplementedError

    def chain_lengths(self) -> list[int]:
        """Длины всех цепочек — сырьё для гистограммы."""
        return [len(bucket) for bucket in self._buckets]


# ---------------------------------------------------------------------------
# 3. Верификация: инварианты, граничные случаи, сверка с dict
# ---------------------------------------------------------------------------


def check_invariants(table: HashTable) -> None:
    """Программная проверка инвариантов таблицы (см. docstring HashTable)."""
    n_buckets = len(table._buckets)
    seen: set[str] = set()
    for i, bucket in enumerate(table._buckets):
        for key, _value in bucket:
            assert table._hash_fn(key, n_buckets) == i, \
                f"ключ {key!r} лежит не в своём бакете"
            assert key not in seen, f"ключ {key!r} встречается дважды"
            seen.add(key)
    assert sum(table.chain_lengths()) == len(table), \
        "сумма длин цепочек не равна размеру таблицы"


def random_keys(rng: random.Random, n: int, length: int = 8) -> list[str]:
    """n различных случайных строковых ключей фиксированной длины."""
    keys: set[str] = set()
    while len(keys) < n:
        keys.add("".join(rng.choice(string.ascii_lowercase) for _ in range(length)))
    return list(keys)


def self_check() -> None:
    """Граничные и типовые случаи + сверка поведения с эталоном dict."""
    t = HashTable()
    assert len(t) == 0
    assert t.get("нет") is None  # отсутствующий ключ -> default
    t.put("a", 1)
    t.put("a", 2)  # обновление значения, а не дубликат
    assert len(t) == 1 and t.get("a") == 2
    t.delete("a")
    assert len(t) == 0
    try:
        t.delete("a")
        raise AssertionError("delete отсутствующего ключа обязан дать KeyError")
    except KeyError:
        pass

    # rehash: после массовой вставки α не превышает порога, ключи не теряются
    t = HashTable()
    rng = random.Random(0)
    for key in random_keys(rng, 100):
        t.put(key, 0)
    assert len(t) == 100 and t.load_factor <= t._max_load_factor
    check_invariants(t)

    # сверка с dict на последовательности случайных операций
    t, etalon = HashTable(), {}
    keys = random_keys(rng, 40)
    for _ in range(2000):
        key, op = rng.choice(keys), rng.random()
        if op < 0.5:
            value = rng.randint(0, 999)
            t.put(key, value)
            etalon[key] = value
        elif op < 0.8:
            assert t.get(key, -1) == etalon.get(key, -1)
        elif key in etalon:
            t.delete(key)
            del etalon[key]
        assert len(t) == len(etalon)
    check_invariants(t)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент: гистограмма длин цепочек для двух хеш-функций
# ---------------------------------------------------------------------------


def chain_length_experiment(seed: int, n_keys: int = 2000, capacity: int = 512) -> None:
    """Распределение длин цепочек: poly_hash против bad_hash на одном наборе ключей."""
    rng = random.Random(seed)
    keys = random_keys(rng, n_keys)
    for name, fn in [("poly_hash", poly_hash), ("bad_hash", bad_hash)]:
        # ёмкость фиксирована (rehash отключён), чтобы гистограммы были сравнимы
        table = HashTable(capacity=capacity, hash_fn=fn, max_load_factor=float("inf"))
        for key in keys:
            table.put(key, 0)
        check_invariants(table)
        lengths = table.chain_lengths()
        print(f"{name}: max цепочка = {max(lengths)}, "
              f"пустых бакетов = {lengths.count(0)} из {capacity}")
        # TODO: построить гистограмму длин цепочек (matplotlib) и включить в отчёт;
        # TODO: объяснить различие распределений качеством хеш-функций.


# ---------------------------------------------------------------------------
# 5. Бенчмарк: среднее время операций от α (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

ALPHAS = [0.1, 0.25, 0.5, 0.75, 1.0, 2.0]
CAPACITY = 4096  # фиксированная ёмкость: α регулируется числом ключей
N_PROBES = 1000  # число операций get в одном замере
REPEATS = 5


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
    """Среднее время get при разных α + сравнение со встроенным dict."""
    rng = random.Random(seed)
    print("\nсреднее время get, мкс/операция:")
    for alpha in ALPHAS:
        n = int(CAPACITY * alpha)
        keys = random_keys(rng, n)
        table = HashTable(capacity=CAPACITY, max_load_factor=float("inf"))
        etalon = {}
        for key in keys:
            table.put(key, 0)
            etalon[key] = 0
        probes = [rng.choice(keys) for _ in range(N_PROBES)]

        def probe_table() -> None:
            for key in probes:
                table.get(key)

        def probe_dict() -> None:
            for key in probes:
                etalon.get(key)

        t_table = bench(probe_table) / N_PROBES * 1e6
        t_dict = bench(probe_dict) / N_PROBES * 1e6
        print(f"  α={alpha:>4}  HashTable={t_table:8.3f}  dict={t_dict:8.3f}")
    # TODO: аналогично замерить put; построить график «время от α»;
    # TODO: в отчёте объяснить рост времени с α и разрыв с dict
    #       (реализация на C, открытая адресация, кэширование хешей).


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    chain_length_experiment(seed)
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
