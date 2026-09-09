"""
tests/test_storage.py
Тесты файлового хранилища JsonTaskStorage с изолированными фикстурами.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from taskflow.exceptions import StorageCorruptedError, StorageError
from taskflow.models import Priority, Status, Task
from taskflow.storage import JsonTaskStorage


def test_storage_initialization_creates_file(tmp_path: Path) -> None:
    """Инициализация хранилища должна создавать директорию и пустой файл."""
    test_file = tmp_path / "subdir" / "tasks.json"
    assert not test_file.exists()

    storage = JsonTaskStorage(file_path=test_file)
    assert test_file.exists()
    assert storage.load_all() == []


def test_storage_save_and_load(tmp_path: Path) -> None:
    """Проверка успешного цикла сохранения и вычитки задач."""
    test_file = tmp_path / "tasks.json"
    storage = JsonTaskStorage(file_path=test_file)

    task1 = Task(title="Первая задача", priority=Priority.HIGH, status=Status.IN_PROGRESS)
    task2 = Task(title="Вторая задача", tags=["cli", "pytest"])
    storage.save_all([task1, task2])

    loaded = storage.load_all()
    assert len(loaded) == 2
    assert loaded[0].id == task1.id
    assert loaded[0].title == "Первая задача"
    assert loaded[0].priority == Priority.HIGH
    assert loaded[1].id == task2.id
    assert loaded[1].tags == ["cli", "pytest"]


def test_storage_corrupted_json(tmp_path: Path) -> None:
    """Повреждённый синтаксис JSON должен вызывать StorageCorruptedError."""
    test_file = tmp_path / "corrupted.json"
    test_file.write_text("{ broken json", encoding="utf-8")

    storage = JsonTaskStorage(file_path=test_file)
    with pytest.raises(StorageCorruptedError, match="Синтаксическая ошибка JSON"):
        storage.load_all()


def test_storage_non_list_root(tmp_path: Path) -> None:
    """JSON, в корне которого не массив, должен вызывать StorageCorruptedError."""
    test_file = tmp_path / "object_root.json"
    test_file.write_text('{"key": "value"}', encoding="utf-8")

    storage = JsonTaskStorage(file_path=test_file)
    with pytest.raises(StorageCorruptedError, match="обязан быть массивом"):
        storage.load_all()


def test_storage_empty_file_returns_empty_list(tmp_path: Path) -> None:
    """Пустой файл должен корректно обрабатываться и возвращать пустой список."""
    test_file = tmp_path / "empty.json"
    test_file.write_text("", encoding="utf-8")

    storage = JsonTaskStorage(file_path=test_file)
    assert storage.load_all() == []


def test_storage_permission_error_raises_storage_error(tmp_path: Path) -> None:
    """Ошибка доступа к файлу должна поднимать StorageError."""
    test_file = tmp_path / "tasks.json"
    storage = JsonTaskStorage(file_path=test_file)

    with patch("builtins.open", side_effect=PermissionError("Permission denied")), pytest.raises(
        StorageError, match="Отказано в доступе"
    ):
        storage.load_all()
