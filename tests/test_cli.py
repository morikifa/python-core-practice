"""
tests/test_cli.py
Интеграционные тесты консольного интерфейса TaskFlow CLI.
"""

from pathlib import Path
from unittest.mock import patch

from taskflow.cli import main


def test_cli_add_and_list(temp_storage_path: Path, capsys) -> None:
    """CLI: добавление задачи и вывод списка."""
    # 1. Добавляем задачу
    exit_code_add = main([
        "--storage", str(temp_storage_path),
        "add", "Написать автотесты",
        "-d", "Покрыть весь CLI тестами",
        "-p", "high",
        "-t", "qa",
    ])
    assert exit_code_add == 0
    captured_add = capsys.readouterr()
    assert "Задача создана" in captured_add.out

    # 2. Выводим список
    exit_code_list = main([
        "--storage", str(temp_storage_path),
        "list",
    ])
    assert exit_code_list == 0
    captured_list = capsys.readouterr()
    assert "Написать автотесты" in captured_list.out
    assert "HIGH" in captured_list.out


def test_cli_done_start_stop_delete_and_stats(temp_storage_path: Path, capsys) -> None:
    """CLI: жизненный цикл задачи (start, stop, done, delete) и статистика."""
    main([
        "--storage", str(temp_storage_path),
        "add", "Сдать экзамен Т-Банка",
        "-p", "critical",
    ])
    captured = capsys.readouterr()
    short_id = captured.out.split("ID=")[1].split()[0]

    # Запускаем таймер
    exit_code_start = main([
        "--storage", str(temp_storage_path),
        "start", short_id,
        "-n", "Решение задач",
    ])
    assert exit_code_start == 0
    assert "Таймер запущен" in capsys.readouterr().out

    # Останавливаем таймер
    exit_code_stop = main([
        "--storage", str(temp_storage_path),
        "stop", short_id,
        "-n", "Контест сдан",
    ])
    assert exit_code_stop == 0
    assert "Таймер остановлен" in capsys.readouterr().out

    # Завершаем задачу
    exit_code_done = main([
        "--storage", str(temp_storage_path),
        "done", short_id,
    ])
    assert exit_code_done == 0

    # Проверяем статистику
    exit_code_stats = main([
        "--storage", str(temp_storage_path),
        "stats",
    ])
    assert exit_code_stats == 0
    captured_stats = capsys.readouterr()
    assert "Завершено (DONE):        1" in captured_stats.out

    # Удаляем задачу
    exit_code_del = main([
        "--storage", str(temp_storage_path),
        "delete", short_id,
    ])
    assert exit_code_del == 0
    assert "Задача удалена" in capsys.readouterr().out


def test_cli_empty_list(temp_storage_path: Path, capsys) -> None:
    """Вывод пустого списка."""
    exit_code = main(["--storage", str(temp_storage_path), "list"])
    assert exit_code == 0
    assert "Список задач пуст." in capsys.readouterr().out


def test_cli_error_handling(temp_storage_path: Path, capsys) -> None:
    """Обработка ожидаемых ошибок в CLI."""
    exit_code = main(["--storage", str(temp_storage_path), "done", "unknown-id"])
    assert exit_code == 1
    assert "Ошибка:" in capsys.readouterr().err


def test_cli_unexpected_exception(temp_storage_path: Path, capsys) -> None:
    """Непредвиденное исключение возвращает код 2."""
    with patch("taskflow.cli.TaskService.list_tasks", side_effect=RuntimeError("Fatal error")):
        exit_code = main(["--storage", str(temp_storage_path), "list"])
        assert exit_code == 2
        assert "Критический сбой:" in capsys.readouterr().err
