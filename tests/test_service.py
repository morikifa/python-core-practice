"""
tests/test_service.py
Тесты сервисного слоя TaskService.
"""

import pytest

from taskflow.exceptions import TaskNotFoundError, ValidationError
from taskflow.models import Priority, Status, Task
from taskflow.service import TaskService
from taskflow.storage import JsonTaskStorage


def test_create_task(service: TaskService) -> None:
    """Создание задачи через сервис должно сохранять её в хранилище."""
    task = service.create_task(
        title="Новая задача",
        description="Подробности",
        priority=Priority.HIGH,
        tags=["pytest", "service"],
    )
    assert task.title == "Новая задача"
    assert task.priority == Priority.HIGH
    assert task.tags == ["pytest", "service"]

    all_tasks = service.list_tasks()
    assert len(all_tasks) == 1
    assert all_tasks[0].id == task.id


def test_get_task_by_exact_id_and_prefix(
    service: TaskService, storage: JsonTaskStorage, sample_tasks: list[Task]
) -> None:
    """Поиск задачи по полному ID и префиксу."""
    storage.save_all(sample_tasks)
    target = sample_tasks[0]

    # Точное совпадение
    found_exact = service.get_task_by_id(target.id)
    assert found_exact.id == target.id

    # Совпадение по префиксу из 8 символов
    found_prefix = service.get_task_by_id(target.id[:8])
    assert found_prefix.id == target.id


def test_get_task_empty_id_raises_validation_error(service: TaskService) -> None:
    """Пустой ID должен вызывать ValidationError."""
    with pytest.raises(ValidationError, match="не может быть пустым"):
        service.get_task_by_id("   ")


def test_get_task_ambiguous_prefix(service: TaskService, storage: JsonTaskStorage) -> None:
    """Неоднозначный префикс должен вызывать ValidationError."""
    task1 = Task(id="abcdef-1111", title="Задача 1")
    task2 = Task(id="abcdef-2222", title="Задача 2")
    storage.save_all([task1, task2])

    with pytest.raises(ValidationError, match="неоднозначен"):
        service.get_task_by_id("abcdef")


def test_get_task_not_found(service: TaskService) -> None:
    """Несуществующий ID должен вызывать TaskNotFoundError."""
    with pytest.raises(TaskNotFoundError, match="не найдена"):
        service.get_task_by_id("non-existing-id")


def test_list_tasks_filtering(
    service: TaskService, storage: JsonTaskStorage, sample_tasks: list[Task]
) -> None:
    """Фильтрация по статусу, приоритету и тегу."""
    storage.save_all(sample_tasks)

    # Фильтр по статусу
    done_tasks = service.list_tasks(status=Status.DONE)
    assert len(done_tasks) == 1
    assert done_tasks[0].title == "Написать документацию"

    # Фильтр по приоритету
    critical_tasks = service.list_tasks(priority=Priority.CRITICAL)
    assert len(critical_tasks) == 1
    assert critical_tasks[0].title == "Реализовать Auth"

    # Фильтр по тегу
    docker_tasks = service.list_tasks(tag="docker")
    assert len(docker_tasks) == 1
    assert docker_tasks[0].title == "Настроить Docker"

    # Поисковый запрос
    searched = service.list_tasks(search_query="auth")
    assert len(searched) == 1
    assert searched[0].title == "Реализовать Auth"

    # Сортировка по приоритету reverse
    sorted_prio = service.list_tasks(sort_by="priority", reverse=True)
    assert sorted_prio[0].priority == Priority.CRITICAL


def test_update_status(
    service: TaskService, storage: JsonTaskStorage, sample_tasks: list[Task]
) -> None:
    """Обновление статуса задачи."""
    storage.save_all(sample_tasks)
    target = sample_tasks[0]
    assert target.status == Status.TODO

    updated = service.update_task_status(target.id, Status.DONE)
    assert updated.status == Status.DONE

    reloaded = service.get_task_by_id(target.id)
    assert reloaded.status == Status.DONE


def test_timer_lifecycle_in_service(
    service: TaskService, storage: JsonTaskStorage, sample_tasks: list[Task]
) -> None:
    """Запуск и остановка таймера через TaskService."""
    storage.save_all(sample_tasks)
    target = sample_tasks[0]

    # Запуск таймера
    updated_task, entry = service.start_task_timer(target.id, note="Начало работы")
    assert updated_task.status == Status.IN_PROGRESS
    assert entry.note == "Начало работы"

    # Остановка таймера
    stopped_task, stopped_entry = service.stop_task_timer(target.id, note="Конец работы")
    assert stopped_entry.end_time is not None
    assert stopped_entry.note == "Конец работы"
    assert stopped_task.total_duration_seconds() >= 0


def test_delete_task(
    service: TaskService, storage: JsonTaskStorage, sample_tasks: list[Task]
) -> None:
    """Удаление задачи из хранилища."""
    storage.save_all(sample_tasks)
    target = sample_tasks[0]

    deleted = service.delete_task(target.id)
    assert deleted.id == target.id

    remaining = service.list_tasks()
    assert len(remaining) == len(sample_tasks) - 1
    assert all(t.id != target.id for t in remaining)


def test_summary_statistics(
    service: TaskService, storage: JsonTaskStorage, sample_tasks: list[Task]
) -> None:
    """Расчёт агрегированной статистики."""
    storage.save_all(sample_tasks)
    stats = service.get_summary_statistics()

    assert stats["total"] == 3
    assert stats["todo"] == 1
    assert stats["in_progress"] == 1
    assert stats["done"] == 1
    assert stats["critical"] == 1
    assert stats["high"] == 1
    assert "total_tracked_seconds" in stats
