"""
Кастомная иерархия исключений для TaskFlow Core.
"""


class TaskFlowError(Exception):
    """Базовое исключение для всех доменных ошибок приложения TaskFlow."""


class TaskNotFoundError(TaskFlowError):
    """Выбрасывается, когда задача с указанным ID не найдена в хранилище."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Задача с идентификатором '{task_id}' не найдена.")


class StorageError(TaskFlowError):
    """Базовое исключение для ошибок персистенса и дискового ввода-вывода."""


class StorageCorruptedError(StorageError):
    """Выбрасывается при повреждении структуры JSON-файла хранилища."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Хранилище данных повреждено: {message}")


class ValidationError(TaskFlowError):
    """Выбрасывается при нарушении контрактов валидации доменных моделей."""
