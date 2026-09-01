#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка Markdown-ссылок и структуры репозитория ФОС «СиАОД, семестр 1».

Использование:
    python scripts/check_links.py                  # внутренние ссылки, якоря, структура
    python scripts/check_links.py --external       # + внешние http(s)-ссылки (предупреждения)
    python scripts/check_links.py --only-external  # только внешние ссылки
    python scripts/check_links.py --strict-external# внешние ссылки считаются ошибками

Что проверяется:
  1. Внутренние ссылки [текст](путь) во всех *.md и markdown-ячейках *.ipynb:
     существование файла и (для ссылок вида file.md#якорь) наличие якоря,
     вычисленного из заголовков по правилам GitHub.
  2. Структура: обязательные файлы; пары kim-NN/rubric-NN в модулях M1–M4,
     Cases и Exam; наличие 10 обязательных разделов в каждом КИМ; единая
     10-балльная шкала (10/8/6/4/0-3) в каждой рубрике.
  3. Согласованность БРС: потолок 100 баллов и порог автомата 70 зафиксированы
     в README, РПД и Exam; упоминаний «120 балл» нет нигде.

Код выхода: 0 — ошибок нет; 1 — найдены ошибки.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "node_modules", ".venv"}

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")

# --- Структурные требования -------------------------------------------------

REQUIRED_FILES = [
    "README.md",
    "LICENSE.md",
    "requirements.txt",
    "docs/rpd.md",
    "docs/reproducibility.md",
    "docs/ai-verification.md",
    "data/kim-indicator-matrix.csv",
    "scripts/generate_data.py",
    "tests/test_environment.py",
    "tests/test_generate_data.py",
    "team/README.md",
    "Exam/README.md",
    "Cases/README.md",
    "M1-intro-and-basic-structures/README.md",
    "M2-sorting/README.md",
    "M3-trees/README.md",
    "M4-search-and-hashing/README.md",
]

KIM_DIRS = [
    "M1-intro-and-basic-structures",
    "M2-sorting",
    "M3-trees",
    "M4-search-and-hashing",
    "Cases",
    "Exam",
]

# Обязательные разделы КИМ (подстроки заголовков, см. README § 2).
KIM_SECTIONS = [
    "Назначение",
    "Привязка к компетенциям",
    "Цель",
    "Условия проведения",
    "Материалы и ресурсы",
    "Задание",
    "Формат сдачи",
    "Критерии и шкала",
    "генеративного ИИ",
    "Вопросы",
]

RUBRIC_LEVELS = ["**10**", "**8**", "**6**", "**4**", "**0–3**"]

BRS_100_FILES = ["README.md", "docs/rpd.md"]
BRS_70_FILES = ["README.md", "docs/rpd.md", "Exam/README.md"]

# ---------------------------------------------------------------------------

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def iter_files(pattern: str):
    for p in sorted(ROOT.rglob(pattern)):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            yield p


def github_slugs(text: str) -> set[str]:
    """Слаги заголовков по правилам GitHub (с учётом дублей -1, -2, ...)."""
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        t = m.group(1).strip().lower()
        t = re.sub(r"[`*\[\]()]", "", t)          # markdown-разметка
        t = re.sub(r"[^\w\s\-]", "", t, flags=re.UNICODE)  # пунктуация
        slug = t.replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        slugs.add(slug if n == 0 else f"{slug}-{n}")
    return slugs


_slug_cache: dict[Path, set[str]] = {}


def slugs_of(path: Path) -> set[str]:
    if path not in _slug_cache:
        try:
            _slug_cache[path] = github_slugs(path.read_text(encoding="utf-8"))
        except OSError:
            _slug_cache[path] = set()
    return _slug_cache[path]


def check_link(source: Path, where: str, target: str, check_external: bool,
               strict_external: bool) -> None:
    if target.startswith(("mailto:", "tel:")):
        return
    if target.startswith(("http://", "https://")):
        if check_external:
            check_url(source, where, target, strict_external)
        return

    path_part, _, anchor = target.partition("#")
    if path_part == "":
        dest = source  # якорь в этом же файле
    else:
        dest = (source.parent / path_part).resolve()
        try:
            dest.relative_to(ROOT)
        except ValueError:
            err(f"{where}: ссылка ведёт за пределы репозитория: {target}")
            return
        if not dest.exists():
            err(f"{where}: файл не найден: {target}")
            return
    if anchor and dest.suffix.lower() == ".md" and dest.exists():
        if anchor not in slugs_of(dest):
            err(f"{where}: якорь не найден: {target}")


def check_url(source: Path, where: str, url: str, strict: bool) -> None:
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "fos-link-checker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.status
    except Exception as exc:  # noqa: BLE001 — сеть недетерминирована
        code = str(exc)
    ok = isinstance(code, int) and code < 400
    if not ok:
        msg = f"{where}: внешняя ссылка недоступна ({code}): {url}"
        err(msg) if strict else warn(msg)


def check_md_links(check_external: bool, strict_external: bool) -> None:
    for md in iter_files("*.md"):
        rel = md.relative_to(ROOT)
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for m in LINK_RE.finditer(line):
                check_link(md, f"{rel}:{lineno}", m.group(1),
                           check_external, strict_external)


def check_ipynb_links() -> None:
    for nb_path in iter_files("*.ipynb"):
        rel = nb_path.relative_to(ROOT)
        try:
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            err(f"{rel}: ноутбук не читается: {exc}")
            continue
        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "markdown":
                continue
            text = "".join(cell.get("source", []))
            for m in LINK_RE.finditer(text):
                check_link(nb_path, f"{rel} (ячейка {i})", m.group(1), False, False)


def check_structure() -> None:
    for f in REQUIRED_FILES:
        if not (ROOT / f).is_file():
            err(f"структура: обязательный файл отсутствует: {f}")

    for d in KIM_DIRS:
        kims = {p.name[len("kim-"):-3] for p in (ROOT / d).glob("kim-*.md")}
        rubrics = {p.name[len("rubric-"):-3] for p in (ROOT / d).glob("rubric-*.md")}
        for suffix in sorted(kims - rubrics):
            err(f"структура: {d}/kim-{suffix}.md без пары rubric-{suffix}.md")
        for suffix in sorted(rubrics - kims):
            err(f"структура: {d}/rubric-{suffix}.md без пары kim-{suffix}.md")

    for kim in iter_files("kim-*.md"):
        rel = kim.relative_to(ROOT)
        text = kim.read_text(encoding="utf-8")
        headings = "\n".join(l for l in text.splitlines() if HEADING_RE.match(l))
        for section in KIM_SECTIONS:
            if section not in headings:
                err(f"{rel}: в КИМ нет раздела «{section}»")

    for rub in iter_files("rubric-*.md"):
        rel = rub.relative_to(ROOT)
        text = rub.read_text(encoding="utf-8")
        for level in RUBRIC_LEVELS:
            if level not in text:
                err(f"{rel}: в рубрике нет уровня шкалы {level}")

    for f in BRS_100_FILES:
        p = ROOT / f
        if p.is_file() and "100" not in p.read_text(encoding="utf-8"):
            err(f"{f}: не зафиксирован потолок БРС 100 баллов")
    for f in BRS_70_FILES:
        p = ROOT / f
        if p.is_file() and "70" not in p.read_text(encoding="utf-8"):
            err(f"{f}: не зафиксирован порог автомата 70 баллов")
    for md in iter_files("*.md"):
        rel = md.relative_to(ROOT)
        if re.search(r"120\s*балл", md.read_text(encoding="utf-8")):
            err(f"{rel}: встречается «120 балл» — БРС утверждена на 100 баллов")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--external", action="store_true",
                    help="проверять внешние http(s)-ссылки (предупреждения)")
    ap.add_argument("--only-external", action="store_true",
                    help="проверять только внешние ссылки")
    ap.add_argument("--strict-external", action="store_true",
                    help="считать недоступные внешние ссылки ошибками")
    args = ap.parse_args()

    only_ext = args.only_external
    check_ext = args.external or args.only_external or args.strict_external

    if not only_ext:
        check_md_links(check_external=False, strict_external=False)
        check_ipynb_links()
        check_structure()
    if check_ext:
        check_md_links(check_external=True, strict_external=args.strict_external)

    for w in warnings:
        print(f"ПРЕДУПРЕЖДЕНИЕ: {w}")
    for e in errors:
        print(f"ОШИБКА: {e}")
    print(f"\nИтого: {len(errors)} ошибок, {len(warnings)} предупреждений")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
