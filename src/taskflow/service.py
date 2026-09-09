"""
src/taskflow/service.py
Сервисный слой бизнес-логики управления задачами и тайм-трекинга TaskFlow.
"""

import logging

from taskflow.exceptions import TaskNotFoundError, ValidationError
from taskflow.models import Priority, Status, Task, TimeEntry
from taskflow.storage import JsonTaskStorage

logger = logging.getLogger(__name__)


class TaskService:
    """
    Сервис бизнес-логики: выполняет CRUD-операции, фильтрацию,
    статистику, манипуляции со статусами и тайм-трекинг задач.
    """

    def __init__(self, storage: JsonTaskStorage) -> None:
        self.storage: JsonTaskStorage = storage

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: list[str] | None = None,
    ) -> Task:
        """
        Создаёт новую задачу, сохраняет в хранилище и возвращает созданный объект.
        """
        task = Task(
            title=title,
            description=description,
            priority=priority,
            tags=tags or [],
        )
        tasks = self.storage.load_all()
        tasks.append(task)
        self.storage.save_all(tasks)
        logger.info("Создана новая задача [ID: %s, Title: '%s']", task.id, task.title)
        return task

    def get_task_by_id(self, task_id: str) -> Task:
        """
        Возвращает задачу по полному ID или уникальному префиксу ID.
        """
        clean_id = task_id.strip()
        if not clean_id:
            raise ValidationError("Идентификатор задачи не может быть пустым.")

        tasks = self.storage.load_all()

        # 1. Поиск по точному совпадению
        for task in tasks:
            if task.id == clean_id:
                return task

        # 2. Поиск по префиксу (например, первые 8 символов UUID)
        matched = [task for task in tasks if task.id.startswith(clean_id)]
        if len(matched) == 1:
            return matched[0]
        if len(matched) > 1:
            raise ValidationError(
                f"Префикс '{clean_id}' неоднозначен и соответствует {len(matched)} задачам."
            )

        raise TaskNotFoundError(clean_id)

    def list_tasks(
        self,
        status: Status | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        reverse: bool = False,
    ) -> list[Task]:
        """
        Возвращает отфильтрованный и отсортированный список задач.
        """
        tasks = self.storage.load_all()

        if status is not None:
            tasks = [t for t in tasks if t.status == status]

        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]

        if tag is not None:
            clean_tag = tag.strip().lower()
            tasks = [t for t in tasks if clean_tag in t.tags]

        if search_query is not None:
            query = search_query.strip().lower()
            tasks = [
                t for t in tasks
                if query in t.title.lower() or query in t.description.lower()
            ]

        # Сортировка по допустимым атрибутам
        allowed_sort_fields = {"created_at", "updated_at", "priority", "status", "title"}
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        if sort_by == "priority":
            priority_weight = {
                Priority.LOW: 1,
                Priority.MEDIUM: 2,
                Priority.HIGH: 3,
                Priority.CRITICAL: 4,
            }
            tasks.sort(key=lambda t: priority_weight[t.priority], reverse=reverse)
        else:
            tasks.sort(key=lambda t: getattr(t, sort_by), reverse=reverse)

        return tasks

    def update_task_status(self, task_id: str, new_status: Status) -> Task:
        """
        Изменяет статус задачи и обновляет метку времени updated_at.
        """
        tasks = self.storage.load_all()
        target_task = self.get_task_by_id(task_id)

        for idx, task in enumerate(tasks):
            if task.id == target_task.id:
                task.status = new_status
                task.touch()
                tasks[idx] = task
                self.storage.save_all(tasks)
                logger.info("Статус задачи %s изменён на %s", task.id, new_status.value)
                return task

        raise TaskNotFoundError(task_id)

    def start_task_timer(self, task_id: str, note: str = "") -> tuple[Task, TimeEntry]:
        """
        Запускает интервал тайм-трекинга для задачи.
        """
        tasks = self.storage.load_all()
        target_task = self.get_task_by_id(task_id)

        for idx, task in enumerate(tasks):
            if task.id == target_task.id:
                entry = task.start_timer(note=note)
                tasks[idx] = task
                self.storage.save_all(tasks)
                logger.info("Таймер задачи %s успешно запущен", task.id)
                return task, entry

        raise TaskNotFoundError(task_id)

    def stop_task_timer(self, task_id: str, note: str = "") -> tuple[Task, TimeEntry]:
        """
        Останавливает активный таймер задачи.
        """
        tasks = self.storage.load_all()
        target_task = self.get_task_by_id(task_id)

        for idx, task in enumerate(tasks):
            if task.id == target_task.id:
                entry = task.stop_timer(note=note)
                tasks[idx] = task
                self.storage.save_all(tasks)
                logger.info("Таймер задачи %s остановлен (длительность: %ds)", task.id, entry.duration_seconds)
                return task, entry

        raise TaskNotFoundError(task_id)

    def delete_task(self, task_id: str) -> Task:
        """
        Удаляет задачу по ID и возвращает удалённый экземпляр.
        """
        tasks = self.storage.load_all()
        target_task = self.get_task_by_id(task_id)

        remaining_tasks = [t for t in tasks if t.id != target_task.id]
        self.storage.save_all(remaining_tasks)
        logger.info("Задача %s успешно удалена", target_task.id)
        return target_task

    def get_summary_statistics(self) -> dict[str, int]:
        """
        Рассчитывает статистические метрики по текущим задачам.
        """
        tasks = self.storage.load_all()
        total_seconds = sum(t.total_duration_seconds() for t in tasks)
        return {
            "total": len(tasks),
            "todo": sum(1 for t in tasks if t.status == Status.TODO),
            "in_progress": sum(1 for t in tasks if t.status == Status.IN_PROGRESS),
            "done": sum(1 for t in tasks if t.status == Status.DONE),
            "cancelled": sum(1 for t in tasks if t.status == Status.CANCELLED),
            "critical": sum(1 for t in tasks if t.priority == Priority.CRITICAL),
            "high": sum(1 for t in tasks if t.priority == Priority.HIGH),
            "total_tracked_seconds": total_seconds,
        }
