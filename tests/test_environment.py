#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke-тест окружения дисциплины (см. docs/reproducibility.md).

Проверяет минимум, необходимый для выполнения лабораторных работ и ДЗ:
версию Python и импортируемость пакетов из requirements.txt. Версии пакетов
проверяются мягко — только сам импорт и наличие атрибута __version__;
диапазоны версий закреплены в requirements.txt и контролируются pip.

Запуск: pytest tests/ (секунды, CPU).
"""
from __future__ import annotations

import importlib
import sys

import pytest

REQUIRED_PACKAGES = ("numpy", "matplotlib", "pytest")


def test_python_version() -> None:
    """Дисциплина требует Python 3.10+ (см. requirements.txt и КИМ)."""
    assert sys.version_info >= (3, 10), (
        f"Требуется Python 3.10+, найден {sys.version.split()[0]}; "
        "переустановите окружение по docs/reproducibility.md"
    )


@pytest.mark.parametrize("name", REQUIRED_PACKAGES)
def test_package_importable(name: str) -> None:
    """Пакет из requirements.txt импортируется и сообщает версию."""
    module = importlib.import_module(name)
    version = getattr(module, "__version__", "")
    assert version, (
        f"Пакет {name} импортирован, но не сообщает __version__; "
        "проверьте установку по requirements.txt"
    )
