# python-core-practice

Рабочий репозиторий тренажёра Python Core и алгоритмов + **система памяти наставника** (`mentor/`).

Это не портфолио-проект, а инструмент ежедневной практики: здесь живут срезы по синтаксису, решения алгоритмических задач и полная история обучения. Портфолио-проекты ведутся отдельными репозиториями (см. `mentor/projects.md`).

## Структура

```
python-core-practice/
├── algorithms/            # задачи по темам: условия, решения, edge cases
│   ├── README.md          # спринт из 12 задач (условия, без решений)
│   ├── prefix-sums/
│   ├── two-pointers/
│   ├── hashmaps/
│   ├── sliding-window/
│   ├── stack/
│   ├── simulation/
│   └── matrix/
├── snippets/              # мини-примеры по темам Python Core (к срезам)
├── mentor/                # ПАМЯТЬ НАСТАВНИКА (читается перед каждым ответом)
│   ├── state.md           # текущее состояние, дедлайны, план, блокеры  ← главный файл
│   ├── progress.md        # проценты по трекам + метрики Middle-Ready
│   ├── projects.md        # реестр и линейка проектов, продакшн-признаки
│   ├── interviews.md      # журнал откликов, банк вопросов, срезы
│   ├── resume.md          # стратегия резюме и позиционирования
│   ├── glossary.md        # термины с объяснением и статусом проверки
│   ├── competitors.md     # анализ рынка и конкурентов
│   ├── quick-wins.md      # лог подтверждённых побед
│   ├── retrospective.md   # Keep / Start / Stop по неделям
│   ├── journal/           # бортжурнал: YYYY-MM-DD.md + TEMPLATE.md
│   └── history/           # неизменяемые архивы исходных данных
└── .gitignore
```

## Правила работы

1. Каждый день — минимум один осмысленный коммит (Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `ci:`).
2. Каждый файл решения содержит docstring: условие, ограничения, **O(время)**, **O(память)**, дата.
3. Код пишется руками. AI — ревьюер и наставник, не автор: сгенерированный фрагмент не принимается, пока каждая строка объяснена (см. Gate-вопросы в `mentor/state.md`).
4. Чужие готовые решения своих задач не смотреть.
5. После каждой сессии обновляются `mentor/state.md`, `mentor/progress.md` и журнал дня.

## Окружение

- Python 3.11+ (`requires-python = ">=3.11"`), pytest, ruff.
- Локальная машина: WSL2 (Ubuntu) на Huawei MateBook D16 2021.
- Секреты — только в `.env`, который в `.gitignore`. Хардкод токенов запрещён.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-cov ruff
ruff check .
pytest -v --cov=. --cov-report=term-missing
```
