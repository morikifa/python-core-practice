"""
src/taskflow/storage.py
Слой персистенса данных: потокобезопасная и атомарная работа с JSON-файлом через pathlib.
"""

import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from taskflow.exceptions import StorageCorruptedError, StorageError
from taskflow.models import Task

logger = logging.getLogger(__name__)


class JsonTaskStorage:
    """
    Файловое JSON-хранилище задач с гарантией атомарной записи (Atomic POSIX Write).
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path: Path = file_path.resolve()
        self._ensure_storage_ready()

    def _ensure_storage_ready(self) -> None:
        """
        Создаёт родительские папки и инициализирует пустой файл [], если он не существует.
        """
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                logger.info("Создание нового файла хранилища: %s", self.file_path)
                self._write_raw_data([])
        except OSError as err:
            raise StorageError(f"Не удалось инициализировать директорию хранилища: {err}") from err

    def _write_raw_data(self, data: list[dict[str, Any]]) -> None:
        """
        Атомарная запись списка словарей во временный файл с последующей подменой.
        Включает вызовы flush() и os.fsync() для 100% гарантии записи на физический диск.
        """
        directory = self.file_path.parent
        try:
            # 1. Временный файл ОБЯЗАН быть в той же директории/томе для атомарного rename
            with NamedTemporaryFile(
                mode="w",
                dir=directory,
                encoding="utf-8",
                delete=False,
                suffix=".tmp",
            ) as temp_file:
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
                # 2. Выталкиваем данные из буфера Python в ОС
                temp_file.flush()
                # 3. Принудительно сбрасываем буфер ядра ОС на физический диск
                os.fsync(temp_file.fileno())
                temp_path = Path(temp_file.name)

            # 4. Атомарная замена целевого файла (POSIX rename)
            temp_path.replace(self.file_path)

            # 5. Синхронизация каталога для фиксации изменений в файловой таблице
            try:
                dir_fd = os.open(str(directory), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            except (OSError, AttributeError):
                pass  # На некоторых ОС/FS fsync директории не поддерживается

        except OSError as err:
            raise StorageError(f"Ошибка ввода-вывода при сохранении данных: {err}") from err

    def load_all(self) -> list[Task]:
        """
        Загружает все задачи из JSON-файла с валидацией целостности структуры.
        """
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file_stream:
                content = file_stream.read().strip()
                if not content:
                    return []
                raw_list = json.loads(content)

            if not isinstance(raw_list, list):
                raise StorageCorruptedError("Корневой элемент JSON обязан быть массивом (list).")

            return [Task.from_dict(item) for item in raw_list]

        except json.JSONDecodeError as err:
            logger.error("Синтаксическая ошибка в JSON файле %s: %s", self.file_path, err)
            raise StorageCorruptedError(f"Синтаксическая ошибка JSON: {err}") from err
        except PermissionError as err:
            raise StorageError(f"Отказано в доступе к файлу хранилища: {err}") from err
        except StorageCorruptedError:
            raise
        except Exception as err:
            logger.error("Ошибка при чтении хранилища: %s", err)
            raise StorageCorruptedError(f"Не удалось прочитать данные: {err}") from err

    def save_all(self, tasks: list[Task]) -> None:
        """
        Сериализует список объектов Task и атомарно сохраняет их на диск.
        """
        raw_data = [task.to_dict() for task in tasks]
        self._write_raw_data(raw_data)
