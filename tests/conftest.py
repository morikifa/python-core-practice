"""
Глобальные фикстуры pytest для тестирования TaskFlow.
"""

from pathlib import Path

import pytest

from taskflow.models import Priority, Status, Task
from taskflow.service import TaskService
from taskflow.storage import JsonTaskStorage


@pytest.fixture
def temp_storage_path(tmp_path: Path) -> Path:
    """Возвращает изолированный путь к временному файлу JSON."""
    return tmp_path / "test_tasks.json"


@pytest.fixture
def storage(temp_storage_path: Path) -> JsonTaskStorage:
    """Инициализирует тестовое изолированное хранилище."""
    return JsonTaskStorage(file_path=temp_storage_path)


@pytest.fixture
def service(storage: JsonTaskStorage) -> TaskService:
    """Инициализирует TaskService с временным хранилищем."""
    return TaskService(storage=storage)


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Набор готовых тестовых задач с различными статусами и приоритетами."""
    return [
        Task(
            title="Настроить Docker",
            description="Подготовить Dockerfile и docker-compose",
            priority=Priority.HIGH,
            status=Status.TODO,
            tags=["devops", "docker"],
        ),
        Task(
            title="Реализовать Auth",
            description="JWT аутентификация через FastAPI",
            priority=Priority.CRITICAL,
            status=Status.IN_PROGRESS,
            tags=["backend", "security"],
        ),
        Task(
            title="Написать документацию",
            description="Оформить README и ADR",
            priority=Priority.LOW,
            status=Status.DONE,
            tags=["docs"],
        ),
    ]
