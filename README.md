# TaskFlow CLI Core

[![CI Pipeline](https://github.com/morikifa/taskflow-cli-core/actions/workflows/ci.yml/badge.svg)](https://github.com/morikifa/taskflow-cli-core/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)](https://pytest.org)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Профессиональный консольный движок управления задачами, тайм-трекинга и агрегации продуктивности с 4-слойной архитектурой, атомарным файловым персистенсом и 91% тестовым покрытием.

---

## 1. Проблема и бизнес-контекст

Разработчики и DevOps-инженеры ежедневно перегружены разрозненными контекстами задач (Jira, GitHub Issues, личные блокноты). Переключение между графическими интерфейсами и браузерами разрушает состояние потока (Flow State) и отнимает до 20% рабочего времени. 

Существующие CLI-утилиты страдают от типичных болезней:
- Отсутствие атомарности записи — при сбое процесса или выключении питания повреждается весь JSON/YAML файл.
- Отсутствие модульного разделения ответственности (бизнес-логика смешана с консольным вводом-выводом).
- Нулевое покрытие тестами и отсутствие валидации типов.

**TaskFlow Core решает эти проблемы:**
1. **Zero-Crash Persistence:** Паттерн Atomic File Write (запись через временный файл и атомарная замена `Path.replace`) гарантирует 100% защиту от повреждения данных.
2. **Clean Layered Architecture:** Строгое разделение слоев (`Domain Models` → `Persistence Storage` → `Service Layer` → `CLI Interface`).
3. **Строгая типизация и валидация:** `dataclasses`, `Enum`, кастомная иерархия исключений `TaskFlowError`.
4. **91%+ Test Coverage:** Полный набор unit- и интеграционных тестов на `pytest` с изолированными фикстурами `tmp_path`.

---

## 2. Технологический стек

- **Язык:** Python 3.11 / 3.12 (строгая типизация `typing`, `dataclasses`, `Enum`).
- **Слой хранения:** Модуль `pathlib.Path`, `tempfile.NamedTemporaryFile`, `json` (Atomic POSIX writes).
- **CLI-интерфейс:** Встроенный модуль `argparse` с подкомандами и поддержкой ANSI-цветов.
- **Тестирование:** `pytest`, `pytest-cov` (покрытие 91%), изолированные фикстуры.
- **Линтинг и форматирование:** `ruff` (максимальная строгость и скорость).
- **Контейнеризация:** Multi-stage `Dockerfile` с запуском под непривилегированным пользователем `appuser`.
- **CI/CD:** GitHub Actions (автоматический линтинг, запуск тестов на матрице Python 3.11/3.12 и проверка сборки).

---

## 3. Архитектура проекта

```
src/taskflow/
├── models.py       # Domain Layer: Task, Priority, Status, ValidationError
├── storage.py      # Persistence Layer: JsonTaskStorage (Atomic File Operations)
├── service.py      # Application Layer: TaskService (CRUD, фильтрация, поиск, статистика)
└── cli.py          # Presentation Layer: argparse CLI, ANSI formatting, exit codes
```

---

## 4. Быстрый старт

### Локальная установка (WSL2 / Linux / macOS)

```bash
# 1. Клонирование репозитория
git clone https://github.com/morikifa/taskflow-cli-core.git
cd taskflow-cli-core

# 2. Создание и активация venv
python3 -m venv .venv
source .venv/bin/activate

# 3. Установка пакета в режиме разработки
pip install -e ".[dev]"
```

### Запуск через Docker

```bash
# Сборка легковесного образа
docker build -t taskflow:latest .

# Запуск команды внутри контейнера
docker run --rm -v $(pwd)/data:/home/appuser/.taskflow taskflow add "Настроить CI/CD" -p critical
docker run --rm -v $(pwd)/data:/home/appuser/.taskflow taskflow list
```

---

## 5. Примеры использования (CLI Commands)

```bash
# 1. Добавить задачу с описанием, приоритетом и тегами
taskflow add "Спроектировать REST API" -d "FastAPI + PostGIS" -p high -t backend -t arch

# 2. Показать список всех задач
taskflow list

# 3. Фильтрация задач по приоритету или тегу
taskflow list -p high
taskflow list -t backend

# 4. Взять задачу в работу по префиксу UUID
taskflow start a1b2c3d4

# 5. Завершить задачу
taskflow done a1b2c3d4

# 6. Посмотреть сводную аналитику
taskflow stats

# 7. Удалить задачу
taskflow delete a1b2c3d4
```

---

## 6. Запуск тестов и замер покрытия

```bash
# Прогон тестов с генерацией отчета о покрытии
pytest -v --cov=src/taskflow --cov-report=term-missing

# Запуск линтера Ruff
ruff check src tests
```

---

## 7. Ограничения текущей версии
- Хранилище оптимизировано для объёмов до 10 000 задач на один файл.
- Для распределённых и многопользовательских сценариев в следующих проектах линейки (`geomarketplace-api`) применяется PostgreSQL и SQLAlchemy 2.0.
