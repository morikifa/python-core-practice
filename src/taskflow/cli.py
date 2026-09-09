"""
src/taskflow/cli.py
Консольный интерфейс (CLI) для TaskFlow Core на базе argparse с поддержкой ANSI и тайм-трекинга.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from taskflow.exceptions import TaskFlowError
from taskflow.models import Priority, Status, Task
from taskflow.service import TaskService
from taskflow.storage import JsonTaskStorage

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def supports_color() -> bool:
    """Проверяет, поддерживает ли текущий терминал вывод ANSI-цветов."""
    if os.getenv("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colorize(text: str, color_code: str) -> str:
    """Оборачивает текст в ANSI-коды, если терминал поддерживает цвет."""
    if supports_color():
        return f"\033[{color_code}m{text}\033[0m"
    return text


def get_default_storage_path() -> Path:
    """Определяет путь к файлу хранилища из переменной окружения или по умолчанию."""
    custom_path = os.getenv("TASKFLOW_STORAGE_PATH")
    if custom_path:
        return Path(custom_path)
    return Path.home() / ".taskflow" / "tasks.json"


def format_task_row(task: Task) -> str:
    """Форматирует строку задачи для табличного вывода в консоль."""
    priority_colors = {
        Priority.LOW: "90",
        Priority.MEDIUM: "34",
        Priority.HIGH: "33",
        Priority.CRITICAL: "91;1",
    }
    status_icons = {
        Status.TODO: "[ ]",
        Status.IN_PROGRESS: "[>]",
        Status.DONE: "[v]",
        Status.CANCELLED: "[x]",
    }

    short_id = task.id[:8]
    tags_repr = f"({', '.join(task.tags)})" if task.tags else ""
    duration_repr = f"[{task.total_duration_seconds()}s]" if task.total_duration_seconds() > 0 else ""
    icon = status_icons.get(task.status, "[?]")

    color_code = priority_colors.get(task.priority, "0")
    priority_str = colorize(f"{task.priority.value.upper():<8}", color_code)

    return f"{icon} {short_id} | {priority_str} | {task.title:<35} {duration_repr} {tags_repr}"


def create_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки с подкомандами."""
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description="TaskFlow CLI Core — Профессиональный менеджер задач и тайм-трекер.",
    )
    parser.add_argument(
        "--storage",
        type=Path,
        default=None,
        help="Пользовательский путь к файлу хранилища JSON.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Подкоманда add
    add_parser = subparsers.add_parser("add", help="Создать новую задачу")
    add_parser.add_argument("title", type=str, help="Заголовок задачи")
    add_parser.add_argument("-d", "--desc", type=str, default="", help="Описание задачи")
    add_parser.add_argument(
        "-p",
        "--priority",
        type=str,
        choices=[p.value for p in Priority],
        default=Priority.MEDIUM.value,
        help="Приоритет задачи (low, medium, high, critical)",
    )
    add_parser.add_argument(
        "-t",
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Тег (можно указывать несколько раз: -t dev -t backend)",
    )

    # 2. Подкоманда list
    list_parser = subparsers.add_parser("list", help="Показать список задач")
    list_parser.add_argument(
        "-s",
        "--status",
        type=str,
        choices=[s.value for s in Status],
        default=None,
        help="Фильтр по статусу",
    )
    list_parser.add_argument(
        "-p",
        "--priority",
        type=str,
        choices=[p.value for p in Priority],
        default=None,
        help="Фильтр по приоритету",
    )
    list_parser.add_argument("-t", "--tag", type=str, default=None, help="Фильтр по тегу")
    list_parser.add_argument("-q", "--query", type=str, default=None, help="Поисковый запрос")
    list_parser.add_argument(
        "--sort",
        type=str,
        choices=["created_at", "updated_at", "priority", "title"],
        default="created_at",
        help="Поле сортировки",
    )
    list_parser.add_argument("--reverse", action="store_true", help="Обратный порядок сортировки")

    # 3. Подкоманда done
    done_parser = subparsers.add_parser("done", help="Отметить задачу как выполненную")
    done_parser.add_argument("task_id", type=str, help="ID задачи или его уникальный префикс")

    # 4. Подкоманда start
    start_parser = subparsers.add_parser("start", help="Взять задачу в работу и запустить таймер")
    start_parser.add_argument("task_id", type=str, help="ID задачи или его уникальный префикс")
    start_parser.add_argument("-n", "--note", type=str, default="", help="Комментарий к сессии работы")

    # 5. Подкоманда stop
    stop_parser = subparsers.add_parser("stop", help="Остановить таймер задачи")
    stop_parser.add_argument("task_id", type=str, help="ID задачи или его уникальный префикс")
    stop_parser.add_argument("-n", "--note", type=str, default="", help="Комментарий к завершению работы")

    # 6. Подкоманда delete
    del_parser = subparsers.add_parser("delete", help="Удалить задачу")
    del_parser.add_argument("task_id", type=str, help="ID задачи или его уникальный префикс")

    # 7. Подкоманда stats
    subparsers.add_parser("stats", help="Показать статистику выполнения задач и трекинга")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI-приложения с обработкой исключений и кодами возврата."""
    parser = create_parser()
    args = parser.parse_args(argv)

    storage_path = args.storage or get_default_storage_path()
    storage = JsonTaskStorage(file_path=storage_path)
    service = TaskService(storage=storage)

    try:
        if args.command == "add":
            task = service.create_task(
                title=args.title,
                description=args.desc,
                priority=Priority(args.priority),
                tags=args.tags,
            )
            success_tag = colorize("[+]", "92")
            print(f"{success_tag} Задача создана: ID={task.id[:8]} | '{task.title}'")

        elif args.command == "list":
            status_enum = Status(args.status) if args.status else None
            priority_enum = Priority(args.priority) if args.priority else None
            tasks = service.list_tasks(
                status=status_enum,
                priority=priority_enum,
                tag=args.tag,
                search_query=args.query,
                sort_by=args.sort,
                reverse=args.reverse,
            )
            if not tasks:
                print("Список задач пуст.")
            else:
                print(f"Всего задач: {len(tasks)}")
                print("-" * 75)
                for task in tasks:
                    print(format_task_row(task))
                print("-" * 75)

        elif args.command == "done":
            task = service.update_task_status(task_id=args.task_id, new_status=Status.DONE)
            success_tag = colorize("[v]", "92")
            print(f"{success_tag} Задача завершена: ID={task.id[:8]} | '{task.title}'")

        elif args.command == "start":
            task, _ = service.start_task_timer(task_id=args.task_id, note=args.note)
            start_tag = colorize("[>]", "94")
            print(f"{start_tag} Таймер запущен: ID={task.id[:8]} | '{task.title}'")

        elif args.command == "stop":
            task, entry = service.stop_task_timer(task_id=args.task_id, note=args.note)
            stop_tag = colorize("[■]", "93")
            print(f"{stop_tag} Таймер остановлен: ID={task.id[:8]} (+{entry.duration_seconds}s)")

        elif args.command == "delete":
            task = service.delete_task(task_id=args.task_id)
            del_tag = colorize("[-]", "91")
            print(f"{del_tag} Задача удалена: ID={task.id[:8]} | '{task.title}'")

        elif args.command == "stats":
            stats = service.get_summary_statistics()
            print("=== Статистика TaskFlow ===")
            print(f"Всего задач:             {stats['total']}")
            print(f"К выполнению (TODO):     {stats['todo']}")
            print(f"В работе (IN_PROG):       {stats['in_progress']}")
            print(f"Завершено (DONE):        {stats['done']}")
            print(f"Отменено:                {stats['cancelled']}")
            print(f"Критических:             {stats['critical']}")
            print(f"Высокий приоритет:       {stats['high']}")
            print(f"Всего времени (секунд):  {stats['total_tracked_seconds']}")

        return 0

    except TaskFlowError as err:
        err_tag = colorize("Ошибка:", "91")
        sys.stderr.write(f"{err_tag} {err}\n")
        return 1
    except Exception as err:  # noqa: BLE001
        err_tag = colorize("Критический сбой:", "91;1")
        sys.stderr.write(f"{err_tag} {err}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
