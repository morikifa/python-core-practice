"""
Доменные модели данных и перечисления TaskFlow Core.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from taskflow.exceptions import ValidationError


class Priority(str, Enum):
    """
    Приоритет задачи.
    Наследуется от str для корректной прямой сериализации в JSON без костылей.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    """
    Жизненный цикл задачи.
    Наследуется от str для упрощения сопоставления со строковыми аргументами CLI.
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class TimeEntry:
    """
    Сущность интервала учёта рабочего времени (тайм-трекинга).

    Поля:
    - id: Уникальный UUID v4 записи таймера.
    - start_time: Временная метка старта в формате UTC ISO-8601.
    - end_time: Временная метка остановки (None, если таймер активен).
    - duration_seconds: Зафиксированная продолжительность в секундах.
    - note: Текстовый комментарий к интервалу работы.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    end_time: str | None = None
    duration_seconds: int = 0
    note: str = ""

    def __post_init__(self) -> None:
        """Валидация типов и консистентности интервала времени."""
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("ID временной записи должен быть непустой строкой.")
        if not isinstance(self.start_time, str) or not self.start_time.strip():
            raise ValidationError("start_time должен быть непустой строкой в формате ISO-8601.")
        if self.end_time is not None and not isinstance(self.end_time, str):
            raise ValidationError("end_time должен быть строкой в формате ISO-8601 или None.")
        if not isinstance(self.duration_seconds, int) or self.duration_seconds < 0:
            raise ValidationError("duration_seconds должен быть неотрицательным целым числом.")

    def stop(self, note: str = "") -> None:
        """Останавливает таймер, фиксирует end_time и вычисляет продолжительность."""
        if self.end_time is not None:
            raise ValidationError("Данный интервал таймера уже остановлен.")
        
        now = datetime.now(UTC)
        self.end_time = now.isoformat()
        if note:
            self.note = note

        try:
            start_dt = datetime.fromisoformat(self.start_time)
            delta = (now - start_dt).total_seconds()
            self.duration_seconds = max(0, int(delta))
        except ValueError as err:
            raise ValidationError(f"Некорректный формат start_time: {self.start_time}") from err

    def to_dict(self) -> dict[str, Any]:
        """Сериализация интервала времени в словарь."""
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimeEntry":
        """Фабричный метод десериализации интервала времени с валидацией."""
        if not isinstance(data, dict):
            raise ValidationError("Входные данные TimeEntry должны быть словарем.")

        if "id" not in data or "start_time" not in data:
            raise ValidationError("В TimeEntry отсутствуют обязательные поля: 'id', 'start_time'.")

        if not isinstance(data["id"], str) or not isinstance(data["start_time"], str):
            raise ValidationError("Поля 'id' и 'start_time' в TimeEntry должны быть строками.")

        end_time = data.get("end_time")
        if end_time is not None and not isinstance(end_time, str):
            raise ValidationError("Поле 'end_time' должно быть строкой или None.")

        duration = data.get("duration_seconds", 0)
        if not isinstance(duration, int):
            raise ValidationError("Поле 'duration_seconds' должно быть целым числом.")

        return cls(
            id=data["id"],
            start_time=data["start_time"],
            end_time=end_time,
            duration_seconds=duration,
            note=str(data.get("note", "")),
        )


@dataclass
class Task:
    """
    Доменная сущность задачи.

    Построчное описание полей:
    - title: Название задачи (не пустое, до 200 символов).
    - description: Детальное описание задачи (опционально).
    - priority: Уровень важности (Priority Enum, по умолчанию MEDIUM).
    - status: Текущий статус выполнения (Status Enum, по умолчанию TODO).
    - tags: Список строковых меток для быстрого поиска и группировки.
    - time_entries: Список интервалов зафиксированного рабочего времени.
    - id: Уникальный 36-символьный UUID v4 идентификатор задачи.
    - created_at: Временная метка создания в формате UTC ISO-8601.
    - updated_at: Временная метка последнего изменения в формате UTC ISO-8601.
    """
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    tags: list[str] = field(default_factory=list)
    time_entries: list[TimeEntry] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    updated_at: str = ""

    def __post_init__(self) -> None:
        """
        Валидация полей сразу после создания объекта датакласса.
        Гарантирует, что невалидный объект не попадёт в систему.
        """
        if not isinstance(self.title, str):
            raise ValidationError("Заголовок задачи должен быть строкой.")

        if not self.updated_at:
            self.updated_at = self.created_at

        cleaned_title = self.title.strip()
        if not cleaned_title:
            raise ValidationError("Заголовок задачи не может быть пустым.")
        if len(cleaned_title) > 200:
            raise ValidationError("Заголовок задачи не должен превышать 200 символов.")
        self.title = cleaned_title

        # Валидация описания
        if not isinstance(self.description, str):
            raise ValidationError("Описание задачи должно быть строкой.")

        # Нормализация тегов: проверка типов, удаление пробелов, нижний регистр, уникальность
        if not isinstance(self.tags, list):
            raise ValidationError("Теги должны быть переданы списком строк.")
        for tag in self.tags:
            if not isinstance(tag, str):
                raise ValidationError(f"Недопустимый тег: {tag}. Теги обязаны быть строками.")
        self.tags = sorted({tag.strip().lower() for tag in self.tags if tag.strip()})

        # Валидация time_entries
        if not isinstance(self.time_entries, list):
            raise ValidationError("time_entries должен быть списком объектов TimeEntry.")
        for entry in self.time_entries:
            if not isinstance(entry, TimeEntry):
                raise ValidationError("Элемент time_entries обязан быть экземпляром TimeEntry.")

        # Валидация типов enum, если они были переданы в виде строк
        if isinstance(self.priority, str) and not isinstance(self.priority, Priority):
            try:
                self.priority = Priority(self.priority.lower())
            except ValueError as err:
                raise ValidationError(f"Недопустимый приоритет: {self.priority}") from err
        elif not isinstance(self.priority, Priority):
            raise ValidationError("Приоритет должен быть экземпляром Priority Enum.")

        if isinstance(self.status, str) and not isinstance(self.status, Status):
            try:
                self.status = Status(self.status.lower())
            except ValueError as err:
                raise ValidationError(f"Недопустимый статус: {self.status}") from err
        elif not isinstance(self.status, Status):
            raise ValidationError("Статус должен быть экземпляром Status Enum.")

    def touch(self) -> None:
        """Обновляет временную метку последней модификации объекта."""
        self.updated_at = datetime.now(UTC).isoformat()

    def start_timer(self, note: str = "") -> TimeEntry:
        """
        Запускает новый интервал тайм-трекинга для задачи.
        Переводит статус в IN_PROGRESS.
        """
        active = self.get_active_timer()
        if active is not None:
            raise ValidationError(
                f"Таймер для задачи '{self.id[:8]}' уже активен (запущен: {active.start_time})."
            )

        entry = TimeEntry(note=note)
        self.time_entries.append(entry)
        self.status = Status.IN_PROGRESS
        self.touch()
        return entry

    def stop_timer(self, note: str = "") -> TimeEntry:
        """Останавливает активный интервал таймера."""
        active = self.get_active_timer()
        if active is None:
            raise ValidationError(f"У задачи '{self.id[:8]}' нет активного таймера.")

        active.stop(note=note)
        self.touch()
        return active

    def get_active_timer(self) -> TimeEntry | None:
        """Возвращает текущую незавершённую сессию тайм-трекинга или None."""
        for entry in self.time_entries:
            if entry.end_time is None:
                return entry
        return None

    def total_duration_seconds(self) -> int:
        """Возвращает суммарную зафиксированную продолжительность работы в секундах."""
        total = sum(entry.duration_seconds for entry in self.time_entries)
        active = self.get_active_timer()
        if active is not None:
            try:
                start_dt = datetime.fromisoformat(active.start_time)
                active_delta = (datetime.now(UTC) - start_dt).total_seconds()
                total += max(0, int(active_delta))
            except ValueError:
                pass
        return total

    def to_dict(self) -> dict[str, Any]:
        """
        Сериализация модели в стандартный словарь Python.
        Значения Enum переводятся в строки через .value.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "time_entries": [entry.to_dict() for entry in self.time_entries],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """
        Фабричный метод десериализации задачи из словаря со строгой валидацией типов.
        """
        if not isinstance(data, dict):
            raise ValidationError("Входные данные задачи должны быть словарем.")

        required_keys = {"id", "title", "created_at"}
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise ValidationError(f"В словаре отсутствуют обязательные поля: {missing_keys}")

        # Строгая проверка типов для предотвращения уязвимостей коэрции типов (C5)
        if not isinstance(data["id"], str):
            raise ValidationError("ID задачи должен быть строкой.")
        if not isinstance(data["title"], str):
            raise ValidationError("Заголовок задачи должен быть строкой.")
        if not isinstance(data["created_at"], str):
            raise ValidationError("created_at задачи должен быть строкой.")

        raw_entries = data.get("time_entries", [])
        if not isinstance(raw_entries, list):
            raise ValidationError("time_entries в словаре должен быть списком.")

        parsed_entries = [
            TimeEntry.from_dict(e) if isinstance(e, dict) else e
            for e in raw_entries
        ]

        raw_priority = data.get("priority", Priority.MEDIUM.value)
        if not isinstance(raw_priority, (Priority, str)):
            raise ValidationError("Некорректный тип приоритета.")

        raw_status = data.get("status", Status.TODO.value)
        if not isinstance(raw_status, (Status, str)):
            raise ValidationError("Некорректный тип статуса.")

        return cls(
            id=data["id"],
            title=data["title"],
            description=str(data.get("description", "")),
            priority=Priority(str(raw_priority)),
            status=Status(str(raw_status)),
            tags=list(data.get("tags", [])),
            time_entries=parsed_entries,
            created_at=data["created_at"],
            updated_at=str(data.get("updated_at", data["created_at"])),
        )
