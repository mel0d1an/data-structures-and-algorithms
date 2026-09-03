#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тесты генератора синтетических данных (scripts/generate_data.py).

Функции генератора вызываются напрямую с уменьшенными объёмами и пишут во
временный каталог pytest (tmp_path), поэтому весь набор тестов выполняется
за секунды. Проверяются три свойства, критичных для дисциплины:

1) детерминированность — одинаковый вариант даёт побайтно одинаковые файлы;
2) корректность logs_answers.json — внедрённые аномалии действительно
   присутствуют в журнале на указанных позициях (самопроверка ДЗ 3);
3) целостность embeddings_ground_truth.json — все указанные id существуют
   в CSV-файлах (самопроверка ДЗ 4).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_data as gd  # noqa: E402

SEED = gd.BASE_SEED + 7  # вариант 7 — произвольный, важна лишь фиксация

# Уменьшенные объёмы для быстрых тестов
SMALL_LOGS = dict(n_events=1_500, n_bursts=2, burst_size=25, n_signatures=2)
SMALL_EMB = dict(n_resumes=60, n_vacancies=60, dim=12, k=5, noise=0.5)
SMALL_TEXTS = dict(length=4_000, n_patterns=6)


def _sha256_by_name(paths: list[Path]) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def _read_log_rows(out_dir: Path) -> list[list[str]]:
    lines = (out_dir / "logs_events.csv").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "timestamp;process;event_type;details"
    rows = [line.split(";") for line in lines[1:]]
    assert all(len(row) == 4 for row in rows), "в строке журнала должно быть 4 поля"
    return rows


def _read_csv_ids(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.split(",", 1)[0] for line in lines[1:]]


def test_same_variant_gives_identical_bytes(tmp_path: Path) -> None:
    """Повторная генерация с тем же seed совпадает побайтно (logs и embeddings)."""
    hashes = []
    for sub in ("run1", "run2"):
        out_dir = tmp_path / sub
        out_dir.mkdir()
        paths = gd.generate_logs(out_dir, SEED, **SMALL_LOGS)
        paths += gd.generate_embeddings(out_dir, SEED, **SMALL_EMB)
        hashes.append(_sha256_by_name(paths))
    assert hashes[0] == hashes[1]


def test_different_variants_give_different_bytes(tmp_path: Path) -> None:
    """Смена варианта меняет содержимое журнала."""
    hashes = []
    for sub, seed in (("v1", SEED), ("v2", SEED + 1)):
        out_dir = tmp_path / sub
        out_dir.mkdir()
        hashes.append(_sha256_by_name(gd.generate_logs(out_dir, seed, **SMALL_LOGS)))
    assert hashes[0]["logs_events.csv"] != hashes[1]["logs_events.csv"]


def test_logs_answers_describe_real_anomalies(tmp_path: Path) -> None:
    """logs_answers.json — валидный JSON, аномалии присутствуют в журнале."""
    gd.generate_logs(tmp_path, SEED, **SMALL_LOGS)
    rows = _read_log_rows(tmp_path)
    answers = json.loads((tmp_path / "logs_answers.json").read_text(encoding="utf-8"))

    bursts = answers["bursts"]
    assert len(bursts) == SMALL_LOGS["n_bursts"]
    for burst in bursts:
        segment = rows[burst["start_index"]:burst["end_index"] + 1]
        assert len(segment) == burst["count"]
        assert {row[2] for row in segment} == {burst["event_type"]}
        t_first = datetime.fromisoformat(segment[0][0])
        t_last = datetime.fromisoformat(segment[-1][0])
        assert (t_last - t_first).total_seconds() <= burst["window_seconds"]
        assert segment[0][0] == burst["t_start"]
        assert segment[-1][0] == burst["t_end"]

    signatures = answers["signatures"]
    assert len(signatures) == SMALL_LOGS["n_signatures"]
    for signature in signatures:
        assert len(signature["indices"]) == len(signature["substrings"])
        assert signature["indices"] == sorted(signature["indices"])
        for index, substring in zip(signature["indices"], signature["substrings"]):
            assert substring in rows[index][3], (
                f"подстрока сигнатуры {signature['name']!r} не найдена "
                f"в details строки {index}"
            )


def test_embeddings_ground_truth_ids_exist(tmp_path: Path) -> None:
    """Все id в embeddings_ground_truth.json существуют в CSV-файлах."""
    gd.generate_embeddings(tmp_path, SEED, **SMALL_EMB)
    resume_ids = _read_csv_ids(tmp_path / "embeddings_resumes.csv")
    vacancy_ids = set(_read_csv_ids(tmp_path / "embeddings_vacancies.csv"))
    ground_truth = json.loads(
        (tmp_path / "embeddings_ground_truth.json").read_text(encoding="utf-8"))

    matches = ground_truth["matches"]
    assert set(matches) == set(resume_ids)
    for resume_id, vacancies in matches.items():
        assert vacancies, f"для {resume_id} не указано ни одной вакансии"
        assert set(vacancies) <= vacancy_ids


def test_manifest_records_variant_and_merges_sets(tmp_path: Path) -> None:
    """manifest.json хранит вариант и накапливает наборы; смена варианта его обнуляет."""
    arrays = gd.generate_arrays(tmp_path, SEED, sizes=(100,))
    gd.write_manifest(tmp_path, 7, SEED, ["arrays"], arrays)
    manifest = json.loads((tmp_path / gd.MANIFEST_NAME).read_text(encoding="utf-8"))
    assert manifest["variant"] == 7
    assert manifest["seed"] == SEED
    assert manifest["sets"] == ["arrays"]
    assert "arrays_random_100.txt" in manifest["files"]

    # тот же вариант, другой набор — сведения накапливаются
    pairs = gd.generate_pairs(tmp_path, SEED, n_keys=50)
    gd.write_manifest(tmp_path, 7, SEED, ["pairs"], pairs)
    manifest = json.loads((tmp_path / gd.MANIFEST_NAME).read_text(encoding="utf-8"))
    assert manifest["sets"] == ["arrays", "pairs"]
    assert {"arrays_random_100.txt", "pairs_keys.txt"} <= set(manifest["files"])

    # другой вариант — манифест начинается заново
    gd.write_manifest(tmp_path, 8, SEED + 1, ["pairs"], pairs)
    manifest = json.loads((tmp_path / gd.MANIFEST_NAME).read_text(encoding="utf-8"))
    assert manifest["variant"] == 8
    assert manifest["sets"] == ["pairs"]
    assert "arrays_random_100.txt" not in manifest["files"]


def test_patterns_occur_in_texts(tmp_path: Path) -> None:
    """Каждый шаблон из patterns.txt встречается в своём тексте."""
    gd.generate_texts(tmp_path, SEED, **SMALL_TEXTS)
    texts = {
        name: (tmp_path / name).read_text(encoding="utf-8")
        for name in ("texts_small_alphabet.txt", "texts_natural.txt")
    }
    lines = (tmp_path / "patterns.txt").read_text(encoding="utf-8").splitlines()
    assert len(lines) == SMALL_TEXTS["n_patterns"]
    for line in lines:
        name, pattern = line.split("\t")
        assert 3 <= len(pattern) <= 30
        assert pattern in texts[name]
