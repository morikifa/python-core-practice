# Реестр проектов и линейка портфолио (Projects Lineup)

**Дата фиксации:** 05.09.2026 (перенос из истории основного чата от 04.09.2026 + аудит)
**Методология:** Project-Driven Development — 70% кодинг проекта / 20% теория по ходу / 10% документация и упаковка.
**Запрет:** todo-поделки «как у всех», calculator, weather, blog, Hello World. Каждый проект обязан иметь продакшн-признаки (принцип №6).

> ⚠️ Каноническое имя Проекта №0 — **`taskflow-cli-core`**. Имена `cli-task-core` и `study-task-manager` (встречались в `state.md` от 04.09) **запрещены** — расхождение R1.

---

## 1. Линейка и график

```
┌────────────────────────────────────────────────────────────────────────┐
│ Проект 0: TaskFlow CLI Core   (04.09.2026 – 20.09.2026)   СТАТУС: 5%   │
│ Стек: Python 3.11+, dataclasses, json/pathlib, pytest >= 80%, GH Actions│
├────────────────────────────────────────────────────────────────────────┤
│ Проект 1: GeoMarketplace API  (21.09.2026 – 15.11.2026)   СТАТУС: 0%   │
│ Стек: FastAPI, PostgreSQL+PostGIS, SQLAlchemy 2.0 async, Redis, MinIO   │
├────────────────────────────────────────────────────────────────────────┤
│ Проект 2: DocuMind AI RAG     (16.11.2026 – 15.01.2027)   СТАТУС: 0%   │
│ Стек: FastAPI, pgvector, LangChain/LlamaIndex, aiogram 3.x, DeepSeek    │
├────────────────────────────────────────────────────────────────────────┤
│ Проект 3: AdPulse Platform    (16.01.2027 – 28.02.2027)   СТАТУС: 0%   │
│ Стек: Django 5, DRF, Celery + Redis, PostgreSQL, Elasticsearch         │
├────────────────────────────────────────────────────────────────────────┤
│ Проект 4: LinkPulse Go Engine (01.03.2027 – 15.04.2027)   СТАТУС: 0%   │
│ Стек: Go, Chi/Gin, Redis, PostgreSQL, Prometheus + Grafana             │
└────────────────────────────────────────────────────────────────────────┘
```

**Правило одновременности (принцип «1–2 проекта»):** активны Проект №0 + тренажёр `python-core-practice` (алгоритмы/синтаксис). Третий активный трек = антипаттерн.

---

## 2. Чек-лист продакшн-признаков (единый для всех проектов)

| Признак | Проект 0 | Проект 1 | Проект 2 | Проект 3 | Проект 4 |
| :--- | :--: | :--: | :--: | :--: | :--: |
| `Dockerfile` | ⬜ (опц. для CLI) | ⬜ | ⬜ | ⬜ | ⬜ |
| `docker-compose.yml` (multi-service) | ⬜ (не требуется) | ⬜ | ⬜ | ⬜ | ⬜ |
| pytest, coverage ≥ 70% | ⬜ цель 80% | ⬜ | ⬜ | ⬜ | ⬜ |
| CI/CD GitHub Actions (lint + test) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| README-кейс (проблема → стек → запуск → демо) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `.gitignore` (секреты не в репо) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| logging вместо print | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `.env` / config-объект, 0 хардкода | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Деплой (публичный URL или артефакт) | ⬜ PyPI/релиз GH | ⬜ | ⬜ | ⬜ | ⬜ |
| Скриншоты/asciinema в README | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

> Заполнять символами ✅ по факту существования артефакта. Пустые чек-боксы = требование добавить.

---

## 3. Проект №0 — `taskflow-cli-core` (АКТИВЕН)

- **Назначение:** консольный движок управления задачами и трекинга времени: файловый персистенс, строгая валидация, фильтрация, отчёты по затраченному времени, покрытие тестами ≥80%.
- **Почему не «обычный todo-list» (фильтр «не клон»):** доменная логика — учёт времени, приоритеты с дедлайнами, переходы состояний через конечный автомат, импорт/экспорт, детерминированные отчёты. Это бизнес-логика, а не CRUD-игрушка.
- **Стек:** Python 3.11+, `dataclasses`, `enum`, `pathlib`, `json`, `argparse`, `logging`, `pytest`, GitHub Actions, `ruff`.
- **Репозиторий:** `morikifa/taskflow-cli-core` — **отдельный публичный репозиторий** (решение ученика от 05.09.2026, расхождение R3 закрыто). `python-core-practice` остаётся тренажёром и памятью наставника.
- **Статус на 05.09.2026:** **5%** — есть только утверждённая структура папок и план. Кода в Git нет. Продакшн-признаки: 0 из 10 (Docker для CLI исключён из обязательных — R2).

### Команды создания репозитория (выполнять на своей машине в WSL2)
```bash
# 1. Создать пустой публичный репозиторий на GitHub (без README, без .gitignore, без лицензии —
#    иначе при первом пуше получишь конфликт историй и придётся делать pull --rebase)
#    В браузере: github.com/new → Owner: morikifa → Name: taskflow-cli-core → Public → Create

# 2. Локальная инициализация
mkdir -p ~/dev/taskflow-cli-core && cd ~/dev/taskflow-cli-core
git init -b main
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-cov ruff
mkdir -p src/taskflow tests docs/journal .github/workflows
touch src/taskflow/__init__.py tests/__init__.py

# 3. .gitignore — взять из python-core-practice/.gitignore (тот же набор правил)
# 4. Первый коммит и пуш
git add .gitignore pyproject.toml README.md
git commit -m "chore: project skeleton and tooling config"
git remote add origin https://github.com/morikifa/taskflow-cli-core.git
git push -u origin main
```
**Проверка после пуша:** открыть `github.com/morikifa/taskflow-cli-core` в режиме инкогнито — репозиторий должен быть виден без логина. Невидимый (private) репозиторий в анкете = минус.

### Структура папок (канон)
```
taskflow-cli-core/
├── .github/workflows/ci.yml        # ruff + pytest + coverage
├── docs/journal/                   # бортжурнал разработки (YYYY-MM-DD.md)
├── src/taskflow/
│   ├── __init__.py
│   ├── models.py                   # dataclasses, Enum статусов/приоритетов
│   ├── storage.py                  # JSON-персистенс через pathlib, атомарная запись
│   ├── service.py                  # бизнес-логика: CRUD, переходы состояний, фильтры
│   └── cli.py                      # argparse: подкоманды add/list/done/report
├── tests/
│   ├── conftest.py                 # фикстуры tmp_path
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_service.py
├── .gitignore
├── pyproject.toml                  # requires-python = ">=3.11"
└── README.md
```

### Очередь реализации (атомарные коммиты)
| # | Шаг | Файлы | Коммит | Проверка понимания (Gate) |
| :-- | :--- | :--- | :--- | :--- |
| 1 | Каркас + конфиг | `.gitignore`, `pyproject.toml`, `README.md` | `chore: project skeleton and tooling config` | G2 |
| 2 | Доменные модели | `models.py` | `feat: task domain models with enums and validation` | G3 |
| 3 | Тесты моделей | `tests/test_models.py` | `test: cover task model validation and state transitions` | G4 |
| 4 | Хранилище | `storage.py` | `feat: json storage with atomic write via pathlib` | G5 |
| 5 | Сервисный слой | `service.py` | `feat: task service with filtering and time tracking` | G6 |
| 6 | CLI | `cli.py` | `feat: argparse cli with add/list/done/report commands` | G7 |
| 7 | CI | `.github/workflows/ci.yml` | `ci: ruff lint and pytest with coverage on push and PR` | G8 |
| 8 | Логирование | `src/taskflow/logging_conf.py` | `feat: structured logging instead of print` | G9 |

### Темы для изучения ПАРАЛЛЕЛЬНО (не больше 2 за раз — принцип №10)
**Сейчас (неделя 4):** (1) `dataclasses` + `typing`; (2) `pathlib` + `json` сериализация.
**Далее:** (3) pytest-фикстуры и `@pytest.mark.parametrize`; (4) `argparse`; (5) GitHub Actions; (6) `logging`.

---

## 4. Проект №1 — `geomarketplace-api` (старт 21.09.2026)

- **Назначение:** асинхронный REST API геолокационного маркетплейса услуг: регистрация исполнителей, поиск заказов в радиусе (PostGIS), кэш популярных запросов в Redis, загрузка фото в S3 (MinIO).
- **Первые 3 часа:** (1) `docker-compose.yml` с PostGIS + Redis; (2) FastAPI-скелет с Pydantic v2 settings; (3) async-подключение через SQLAlchemy 2.0 (asyncpg).
- **Репозиторий:** `morikifa/geomarketplace-api`
- **Структура:**
```
geomarketplace-api/
├── .github/workflows/ci.yml
├── docker/{Dockerfile,docker-compose.yml}   # App + PostGIS + Redis + MinIO
├── docs/{journal,adr}/
├── src/{core,models,schemas,repositories,services,api/v1,main.py}
├── tests/
├── .env.example
├── .gitignore
└── README.md
```
- **Первый коммит:** `feat: docker compose with postgis, async database engine and basic healthcheck`
- **Темы параллельно:** asyncio (Event Loop, coroutines); FastAPI + Pydantic v2; SQL (JOIN, GROUP BY, индексы, `ST_DWithin`, `ST_Distance`); SQLAlchemy 2.0 async + Alembic; Redis (TTL, инвалидация кэша); Docker/Compose.
- **Продуктовый риск:** PostGIS + async + Redis + MinIO = 4 новые технологии. Нарушение принципа №10. **Решение:** вводить по одной: неделя 1 — Docker+PostGIS, неделя 2 — FastAPI+SQLAlchemy, неделя 3 — Redis, неделя 4 — MinIO/PostGIS-запросы.

---

## 5. Проект №2 — `documind-ai-rag` (старт 16.11.2026)

- **Назначение:** RAG-сервис (Retrieval-Augmented Generation — генерация ответа с опорой на найденные фрагменты документов) + Telegram-бот для семантического поиска по закрытой технической документации.
- **Первые 3 часа:** (1) PostgreSQL + `pgvector` в Docker; (2) модуль чанкинга markdown/pdf; (3) эмбеддинги через LLM-API + косинусное сходство.
- **Репозиторий:** `morikifa/documind-ai-rag`
- **Структура:** `bot/` (aiogram 3.x), `src/rag/{ingest,vector_store,generator}.py`, `src/api/`, `src/core/`, `docker-compose.yml`, `README.md`.
- **Первый коммит:** `feat: document parser, chunking pipeline and pgvector integration`
- **Темы параллельно:** векторные эмбеддинги и косинусное сходство; pgvector; LLM API (стриминг, rate-limits, retries, обработка ошибок); aiogram 3.x; промпт-инжиниринг (few-shot, guardrails против галлюцинаций).
- **Бюджет:** LLM API платный. Лимит 0–3000 ₽/мес → использовать DeepSeek/локальные эмбеддинги (`sentence-transformers`) и кэш ответов в Redis. Фиксировать траты в journal.

---

## 6. Проект №3 — `adpulse-platform` (старт 16.01.2027)

- **Назначение:** доска объявлений: категории, модерация, фоновые задачи (Celery), полнотекстовый поиск. Закрывает требование рынка «Django/DRF».
- **Первые 3 часа:** (1) Django 5 + кастомная модель пользователя (`AbstractUser`); (2) DRF + JWT + PostgreSQL; (3) Celery + Redis для фоновых email и аналитики.
- **Репозиторий:** `morikifa/adpulse-platform`
- **Первый коммит:** `feat: django 5 setup with custom user model, drf and celery worker`
- **Темы параллельно:** Django ORM (QuerySets, `select_related`, `prefetch_related`, Q/F); Celery + Celery Beat; SimpleJWT и permissions.
- **Противоречие графику:** старт 16.01.2027 при дате окончания Проекта №2 15.01.2027 — ноль буфера. Переносы фиксировать в `state.md` §5 как отклонение в днях.

---

## 7. Проект №4 — `linkpulse-go-engine` (старт 01.03.2027)

- **Назначение:** высоконагруженный микросервис сокращения URL, редиректов и метрик в реальном времени на Go. Второй слой резюме (производительность, конкурентность).
- **Первые 3 часа:** (1) `go mod init`; (2) HTTP-роутер Chi/Gin + Redis-кэш; (3) Base62-кодирование коротких хэшей.
- **Репозиторий:** `morikifa/linkpulse-go-engine`
- **Первый коммит:** `feat: go http server, base62 encoding and redis cache layer`
- **Темы параллельно:** синтаксис и модель памяти Go (структуры, интерфейсы, указатели); конкурентность (goroutines, channels, `sync.Mutex`, WaitGroup); Prometheus + Grafana.
- **Конфликт:** в линейке Проекта №3 окончание 28.02.2027, старт №4 01.03.2027 — ок. Но Go с месяца 8 (апрель 2027) по резюме №2 vs март 2027 по линейке → расхождение 1 месяц. Приоритет: линейка (март).

---

## 8. Тренажёр `python-core-practice` (не проект, а инструмент)

- **Назначение:** ежедневные алгоритмические задачи и срезы Python Core. Не входит в портфолио как «проект», но даёт публичную историю коммитов (нужно для анкеты Т-Банка и для вкладки Contributions).
- **Структура:** `algorithms/<тема>/task_XX.py` + `tests/`, `snippets/`, `mentor/` (память).
- **Правило:** каждый файл решения содержит docstring с (а) условием, (б) сложностью по времени и памяти, (в) датой.
