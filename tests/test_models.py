"""
Тесты доменных моделей и валидации TaskFlow.
"""

import pytest

from taskflow.exceptions import ValidationError
from taskflow.models import Priority, Status, Task, TimeEntry


def test_task_creation_defaults() -> None:
    """Проверка генерации значений по умолчанию."""
    task = Task(title="Изучить Pytest")
    assert task.title == "Изучить Pytest"
    assert task.description == ""
    assert task.priority == Priority.MEDIUM
    assert task.status == Status.TODO
    assert task.tags == []
    assert task.time_entries == []
    assert len(task.id) == 36
    assert task.created_at == task.updated_at


def test_empty_title_validation() -> None:
    """Пустой заголовок должен приводить к ValidationError."""
    with pytest.raises(ValidationError, match="не может быть пустым"):
        Task(title="   ")


def test_title_type_validation() -> None:
    """Нестроковый заголовок должен приводить к ValidationError."""
    with pytest.raises(ValidationError, match="должен быть строкой"):
        Task(title=12345)  # type: ignore


def test_title_length_validation() -> None:
    """Заголовок свыше 200 символов должен приводить к ValidationError."""
    long_title = "A" * 201
    with pytest.raises(ValidationError, match="не должен превышать 200 символов"):
        Task(title=long_title)


def test_invalid_description_type() -> None:
    """Нестроковое описание должно вызывать ValidationError."""
    with pytest.raises(ValidationError, match="Описание задачи должно быть строкой"):
        Task(title="Тест", description=123)  # type: ignore


def test_tags_normalization() -> None:
    """Теги должны нормализоваться: нижний регистр, трим, уникальность."""
    task = Task(title="Тест тегов", tags=[" Python ", "python", "FASTAPI ", ""])
    assert task.tags == ["fastapi", "python"]


def test_invalid_tags_type() -> None:
    """Некорректный тип тегов должен приводить к ValidationError."""
    with pytest.raises(ValidationError, match="Теги должны быть переданы списком"):
        Task(title="Тест", tags="не список")  # type: ignore

    with pytest.raises(ValidationError, match="Теги обязаны быть строками"):
        Task(title="Тест", tags=["valid", 123])  # type: ignore


def test_invalid_time_entries_type() -> None:
    """Некорректный тип time_entries должен приводить к ValidationError."""
    with pytest.raises(ValidationError, match="time_entries должен быть списком"):
        Task(title="Тест", time_entries="not a list")  # type: ignore

    with pytest.raises(ValidationError, match="обязан быть экземпляром TimeEntry"):
        Task(title="Тест", time_entries=["not_entry"])  # type: ignore


def test_invalid_priority_and_status() -> None:
    """Недопустимые значения Priority и Status должны вызывать ValidationError."""
    with pytest.raises(ValidationError, match="Недопустимый приоритет"):
        Task(title="Тест", priority="invalid_priority")  # type: ignore

    with pytest.raises(ValidationError, match="Недопустимый статус"):
        Task(title="Тест", status="invalid_status")  # type: ignore

    with pytest.raises(ValidationError, match="Приоритет должен быть экземпляром Priority"):
        Task(title="Тест", priority=123)  # type: ignore

    with pytest.raises(ValidationError, match="Статус должен быть экземпляром Status"):
        Task(title="Тест", status=123)  # type: ignore


def test_task_touch_updates_timestamp() -> None:
    """Вызов touch() обязан изменять updated_at."""
    task = Task(title="Тест времени")
    initial_updated = task.updated_at
    task.touch()
    assert task.updated_at >= initial_updated


def test_time_entry_basic_and_stop() -> None:
    """Проверка жизненного цикла TimeEntry."""
    entry = TimeEntry(note="Разработка API")
    assert entry.end_time is None
    assert entry.duration_seconds == 0
    assert entry.note == "Разработка API"

    entry.stop(note="Завершено")
    assert entry.end_time is not None
    assert entry.note == "Завершено"
    assert entry.duration_seconds >= 0

    with pytest.raises(ValidationError, match="уже остановлен"):
        entry.stop()


def test_time_entry_validation_errors() -> None:
    """Проверка валидации полей TimeEntry."""
    with pytest.raises(ValidationError, match="ID временной записи"):
        TimeEntry(id="")

    with pytest.raises(ValidationError, match="start_time должен быть непустой строкой"):
        TimeEntry(start_time="")

    with pytest.raises(ValidationError, match="end_time должен быть строкой"):
        TimeEntry(end_time=12345)  # type: ignore

    with pytest.raises(ValidationError, match="duration_seconds должен быть"):
        TimeEntry(duration_seconds=-10)

    # Некорректный формат start_time при stop
    bad_entry = TimeEntry(start_time="не_дата")
    with pytest.raises(ValidationError, match="Некорректный формат start_time"):
        bad_entry.stop()


def test_time_entry_serialization_roundtrip() -> None:
    """Сериализация и десериализация TimeEntry."""
    entry = TimeEntry(note="Тест", duration_seconds=120)
    data = entry.to_dict()
    restored = TimeEntry.from_dict(data)

    assert restored.id == entry.id
    assert restored.start_time == entry.start_time
    assert restored.duration_seconds == 120
    assert restored.note == "Тест"


def test_time_entry_from_dict_invalid() -> None:
    """Проверка десериализации невалидных словарей TimeEntry."""
    with pytest.raises(ValidationError, match="должны быть словарем"):
        TimeEntry.from_dict("not dict")  # type: ignore

    with pytest.raises(ValidationError, match="отсутствуют обязательные поля"):
        TimeEntry.from_dict({"note": "нет id и start_time"})

    with pytest.raises(ValidationError, match="должны быть строками"):
        TimeEntry.from_dict({"id": 123, "start_time": "2026-09-06T12:00:00Z"})

    with pytest.raises(ValidationError, match="end_time.*должно быть строкой"):
        TimeEntry.from_dict({"id": "abc", "start_time": "2026-09-06", "end_time": 123})

    with pytest.raises(ValidationError, match="duration_seconds.*целым числом"):
        TimeEntry.from_dict({"id": "abc", "start_time": "2026-09-06", "duration_seconds": "invalid"})


def test_task_time_tracking_methods() -> None:
    """Тестирование start_timer, stop_timer, total_duration_seconds."""
    task = Task(title="Задача с таймером")
    assert task.get_active_timer() is None
    assert task.total_duration_seconds() == 0

    entry = task.start_timer(note="Старт работы")
    assert task.status == Status.IN_PROGRESS
    assert task.get_active_timer() == entry
    assert task.total_duration_seconds() >= 0

    # Попытка запустить второй таймер без остановки первого
    with pytest.raises(ValidationError, match="уже активен"):
        task.start_timer()

    stopped = task.stop_timer(note="Финиш работы")
    assert stopped.id == entry.id
    assert task.get_active_timer() is None
    assert task.total_duration_seconds() >= 0

    # Попытка остановить, когда активного таймера нет
    with pytest.raises(ValidationError, match="нет активного таймера"):
        task.stop_timer()


def test_serialization_roundtrip() -> None:
    """Сериализация в dict и десериализация обратно должны сохранять все поля."""
    entry = TimeEntry(note="Тестовый лог", duration_seconds=300)
    original = Task(
        title="Полный тест",
        description="Детали задачи",
        priority=Priority.CRITICAL,
        status=Status.IN_PROGRESS,
        tags=["core", "test"],
        time_entries=[entry],
    )
    data = original.to_dict()
    restored = Task.from_dict(data)

    assert restored.id == original.id
    assert restored.title == original.title
    assert restored.description == original.description
    assert restored.priority == original.priority
    assert restored.status == original.status
    assert restored.tags == original.tags
    assert len(restored.time_entries) == 1
    assert restored.time_entries[0].note == "Тестовый лог"
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at


def test_from_dict_invalid_data() -> None:
    """Некорректный тип данных словаря должен вызывать ValidationError."""
    with pytest.raises(ValidationError, match="должны быть словарем"):
        Task.from_dict("не словарь")  # type: ignore

    with pytest.raises(ValidationError, match="отсутствуют обязательные поля"):
        Task.from_dict({"description": "нет title и id"})

    with pytest.raises(ValidationError, match="ID задачи должен быть строкой"):
        Task.from_dict({"id": 123, "title": "Заголовок", "created_at": "2026-09-06"})

    with pytest.raises(ValidationError, match="Заголовок задачи должен быть строкой"):
        Task.from_dict({"id": "uuid", "title": 12345, "created_at": "2026-09-06"})

    with pytest.raises(ValidationError, match="created_at задачи должен быть строкой"):
        Task.from_dict({"id": "uuid", "title": "Заголовок", "created_at": 12345})

    with pytest.raises(ValidationError, match="time_entries в словаре должен быть списком"):
        Task.from_dict({"id": "uuid", "title": "Заголовок", "created_at": "2026-09-06", "time_entries": "bad"})

    with pytest.raises(ValidationError, match="Некорректный тип приоритета"):
        Task.from_dict({"id": "uuid", "title": "Заголовок", "created_at": "2026-09-06", "priority": 999})

    with pytest.raises(ValidationError, match="Некорректный тип статуса"):
        Task.from_dict({"id": "uuid", "title": "Заголовок", "created_at": "2026-09-06", "status": 999})
