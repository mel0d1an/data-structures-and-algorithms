#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 7. Сравнительный анализ КМП, Рабина–Карпа и Бойера–Мура — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-07 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Соглашения:
- каждая функция поиска возвращает пару (occurrences, comparisons):
  список ВСЕХ индексов вхождений шаблона (включая перекрывающиеся,
  по возрастанию) и число выполненных сравнений символов;
- пустой шаблон считаем не встречающимся: возвращаем ([], 0);
- таблицу плохого символа стройте словарём {символ: индекс}, а не списком
  на 256 позиций — тексты могут содержать произвольные символы Юникода.

Запуск: python lab07-substring-search-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска подстрок (реализуются вручную, без re и str.find
#    в основной части; str.find используется только в эталоне для сверки)
# ---------------------------------------------------------------------------


def naive_search(text: str, pattern: str) -> tuple[list[int], int]:
    """Наивный поиск со сдвигом на одну позицию. Ожидаемая сложность: TODO.

    Эталон для сверки остальных алгоритмов: прост настолько, что в его
    корректности легко убедиться. Считайте каждое сравнение символов.
    """
    # TODO: двойной цикл; прерывать внутренний цикл при первом несовпадении
    raise NotImplementedError


def prefix_function(pattern: str) -> list[int]:
    """Префикс-функция шаблона: pi[i] — длина наибольшего собственного
    префикса подстроки pattern[:i+1], совпадающего с её суффиксом.

    Ожидаемая сложность построения: TODO (обосновать в отчёте).
    """
    # TODO: реализовать за линейное время (переходы по pi при несовпадении)
    raise NotImplementedError


def kmp_search(text: str, pattern: str) -> tuple[list[int], int]:
    """Поиск Кнута–Морриса–Пратта. Ожидаемая сложность: TODO.

    После найденного вхождения продолжайте по префикс-функции —
    перекрывающиеся вхождения не должны теряться.
    """
    # TODO: использовать prefix_function; считать сравнения символов
    raise NotImplementedError


def rabin_karp_search(text: str, pattern: str,
                      base: int = 256, mod: int = 1_000_000_007) -> tuple[list[int], int]:
    """Поиск Рабина–Карпа с полиномиальным хешем по модулю mod.

    Хеш окна пересчитывается за O(1) при сдвиге на один символ.
    При совпадении хешей ОБЯЗАТЕЛЬНА посимвольная проверка окна:
    равенство хешей не гарантирует равенства строк (коллизии).
    Ожидаемая сложность: TODO (средний и худший случаи).
    """
    # TODO: хеш шаблона и первого окна; скользящий пересчёт; проверка окна
    raise NotImplementedError


def bad_char_table(pattern: str) -> dict[str, int]:
    """Таблица плохого символа: для каждого символа шаблона — индекс его
    последнего вхождения в pattern. Используется Бойером–Муром для сдвига.
    """
    # TODO: один проход по шаблону
    raise NotImplementedError


def boyer_moore_search(text: str, pattern: str) -> tuple[list[int], int]:
    """Поиск Бойера–Мура: сравнение с конца шаблона, сдвиг по эвристике
    плохого символа (сдвиг всегда не меньше 1).

    Эвристика хорошего суффикса — дополнительное требование уровня «10»
    рубрики; добавьте её отдельной таблицей и берите максимум сдвигов.
    Ожидаемая сложность: TODO (средний и худший случаи).
    """
    # TODO: использовать bad_char_table; считать сравнения символов
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------


def reference_occurrences(text: str, pattern: str) -> list[int]:
    """Эталон из стандартной библиотеки: все вхождения через str.find
    с шагом 1 (перекрывающиеся вхождения учитываются)."""
    if not pattern:
        return []
    result = []
    pos = text.find(pattern)
    while pos != -1:
        result.append(pos)
        pos = text.find(pattern, pos + 1)
    return result


def self_check() -> None:
    """Граничные и типовые случаи + сверка всех алгоритмов с эталоном."""
    # эталон сам по себе должен вести себя ожидаемо
    assert reference_occurrences("aaaa", "aa") == [0, 1, 2]
    assert reference_occurrences("abc", "abcd") == []

    # префикс-функция: классические примеры (проверьте вручную на бумаге)
    assert prefix_function("abcabcd") == [0, 0, 0, 1, 2, 3, 0]
    assert prefix_function("aabaaab") == [0, 1, 0, 1, 2, 2, 3]

    algorithms = [naive_search, kmp_search, rabin_karp_search, boyer_moore_search]
    for search in algorithms:
        name = search.__name__
        occ, _ = search("aaaa", "aa")
        assert occ == [0, 1, 2], f"{name}: перекрывающиеся вхождения теряются"
        occ, _ = search("abc", "abc")
        assert occ == [0], f"{name}: шаблон, равный тексту"
        occ, _ = search("abc", "abcd")
        assert occ == [], f"{name}: шаблон длиннее текста"
        occ, _ = search("", "a")
        assert occ == [], f"{name}: пустой текст"
        occ, _ = search("abc", "")
        assert occ == [], f"{name}: пустой шаблон (инвариант заготовки)"

    # сверка с эталоном на случайных строках над малым алфавитом:
    # короткий алфавит провоцирует и перекрытия, и коллизии хешей
    rng = random.Random(0)
    for _ in range(300):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(1, 60)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        expected = reference_occurrences(text, pattern)
        for search in algorithms:
            occ, comparisons = search(text, pattern)
            assert occ == expected, (
                f"{search.__name__}: text={text!r}, pattern={pattern!r}, "
                f"получено {occ}, ожидалось {expected}"
            )
            assert comparisons >= 0
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Данные по варианту и бенчмарк (методика — docs/reproducibility.md;
#    полные наборы по варианту генерирует scripts/generate_data.py)
# ---------------------------------------------------------------------------

TEXT_SIZE = 100_000
PATTERN_LENGTHS = [4, 16, 64]
REPEATS = 5

# небольшой лексикон для естественно-подобного текста (частоты символов
# и длины слов ближе к обычному тексту, чем равномерный случайный шум)
LEXICON = [
    "data", "search", "pattern", "index", "hash", "log", "event", "system",
    "error", "server", "signal", "buffer", "stream", "packet", "record",
]


def make_small_alphabet_text(rng: random.Random, length: int) -> str:
    """Текст над малым алфавитом {a, b} — худший режим для наивного поиска."""
    return "".join(rng.choice("ab") for _ in range(length))


def make_natural_text(rng: random.Random, length: int) -> str:
    """Естественно-подобный текст: случайные слова лексикона через пробел."""
    words = []
    total = 0
    while total < length:
        word = rng.choice(LEXICON)
        words.append(word)
        total += len(word) + 1
    return " ".join(words)[:length]


def plant_pattern(rng: random.Random, text: str, pattern: str, count: int) -> str:
    """Вставить count гарантированных вхождений шаблона в копию текста."""
    chars = list(text)
    for _ in range(count):
        pos = rng.randrange(0, len(chars) - len(pattern) + 1)
        chars[pos:pos + len(pattern)] = pattern
    return "".join(chars)


def bench(search, text: str, pattern: str) -> float:
    """Медиана времени выполнения search(text, pattern) по REPEATS запускам."""
    search(text, pattern)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        search(text, pattern)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    texts = {
        "малый алфавит (ab)": make_small_alphabet_text(rng, TEXT_SIZE),
        "естественно-подобный": make_natural_text(rng, TEXT_SIZE),
    }
    algorithms = [
        ("наивный", naive_search),
        ("КМП", kmp_search),
        ("Рабин–Карп", rabin_karp_search),
        ("Бойер–Мур", boyer_moore_search),
    ]
    for text_name, text in texts.items():
        for m in PATTERN_LENGTHS:
            # шаблон берём из самого текста (вхождение гарантировано)
            # и дополнительно вставляем ещё несколько копий
            start = rng.randrange(0, len(text) - m + 1)
            pattern = text[start:start + m]
            sample = plant_pattern(rng, text, pattern, 5)
            print(f"\nТекст: {text_name}, |T| = {len(sample)}, |P| = {m}")
            for name, search in algorithms:
                occurrences, comparisons = search(sample, pattern)
                t = bench(search, sample, pattern)
                print(f"  {name:<12} вхождений = {len(occurrences):>5}  "
                      f"сравнений = {comparisons:>10}  t = {t:.6f} c")
    # TODO: свести результаты в таблицы/графики (сравнения и время
    #       в зависимости от длины шаблона и типа текста);
    # TODO: сопоставить наблюдения с теоретическими оценками и написать
    #       отчёт о применимости: когда выбирать КМП, Рабина–Карпа,
    #       Бойера–Мура (размер алфавита, длина шаблона, характер текста).


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
