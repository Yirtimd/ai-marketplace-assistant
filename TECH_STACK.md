# TECH_STACK.md

# Технологический стек AI Marketplace Assistant

Этот документ фиксирует все технологические решения проекта, версии библиотек и архитектурные выборы.

**Цель:** Избежать проблем со сменой библиотек и обеспечить стабильность разработки.

**Правило:** Любое изменение технологического стека должно быть задокументировано в этом файле с указанием причины и даты изменения.

---

## Версии языков и runtime

| Технология | Версия | Причина выбора | Дата фиксации |
|------------|--------|----------------|---------------|
| **Python** | 3.11+ | Современный синтаксис, улучшенная производительность, async support | 2026-03-09 |
| **Node.js** | 18+ LTS | Для Electron (desktop app), стабильная LTS версия | 2026-03-28 |

---

## Backend Stack

### Web Framework

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **FastAPI** | 0.109.0 | Django, Flask | Современный async фреймворк, автогенерация OpenAPI, type hints, высокая производительность | ✅ Зафиксировано |
| **Uvicorn** | 0.27.0 | Gunicorn, Hypercorn | ASGI сервер с отличной производительностью, полная поддержка FastAPI | ✅ Зафиксировано |

**Решение:** FastAPI + Uvicorn — основной стек для API. **НЕ МЕНЯТЬ**.

---

### ORM и Database Layer

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **SQLAlchemy** | 2.0.25 | Django ORM, Tortoise ORM, Peewee | Мощный ORM с поддержкой async, декларативные модели, миграции через Alembic | ✅ Зафиксировано |
| **Asyncpg** | 0.29.0 | Psycopg3 | Самый быстрый async драйвер для PostgreSQL | ✅ Зафиксировано |
| **Psycopg2-binary** | 2.9.9 | - | Синхронный драйвер для совместимости и утилит | ✅ Зафиксировано |
| **Alembic** | 1.13.1 | - | Стандартный инструмент миграций для SQLAlchemy | ✅ Зафиксировано |

**Решение:** SQLAlchemy 2.0 с async support — основной ORM. **НЕ МЕНЯТЬ**.

**Архитектурные решения:**
- Использовать декларативный стиль (`DeclarativeBase`)
- Async session для всех операций в API
- Sync session только для Celery tasks и утилит
- Connection pooling: `pool_size=5`, `max_overflow=10`

---

### Database

| База данных | Версия | Альтернативы | Причина выбора | Статус |
|-------------|--------|--------------|----------------|--------|
| **PostgreSQL** | 16+ | MySQL, MongoDB | Надежность, ACID, jsonb поддержка, полнотекстовый поиск, индексы | ✅ Зафиксировано |
| **Redis** | 7+ | Memcached, KeyDB | Высокая производительность, поддержка различных структур данных, pub/sub | ✅ Зафиксировано |

**Решение:** PostgreSQL + Redis — основной storage stack. **НЕ МЕНЯТЬ**.

**Использование:**
- **PostgreSQL** — основные данные (users, shops, products, sales, reviews, tasks, events)
- **Redis** — кеш, очереди задач, временное состояние, rate limiting

---

### Task Queue

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **Celery** | 5.3.6 | RQ, Dramatiq, Huey | Зрелое решение, поддержка периодических задач, мониторинг через Flower | ✅ Зафиксировано |
| **Flower** | 2.0.1 | - | Веб-интерфейс для мониторинга Celery | ✅ Зафиксировано |

**Решение:** Celery + Redis (broker) — система фоновых задач. **НЕ МЕНЯТЬ**.

**Конфигурация:**
- Broker: Redis (database 1)
- Result Backend: Redis (database 2)
- Периодические задачи через Celery Beat

---

### AI Framework

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **LangChain** | 0.1.4 | LlamaIndex, Haystack | Богатая экосистема, поддержка множества LLM, инструменты для агентов | ✅ Зафиксировано |
| **LangGraph** | 0.0.20 | - | Построение сложных AI workflows, state management, граф выполнения | ✅ Зафиксировано |
| **OpenAI** | 1.10.0 | - | Официальный клиент OpenAI API (GPT-4, DALL-E, Whisper) | ✅ Зафиксировано |
| **Anthropic** | 0.9.0 | - | Официальный клиент Anthropic API (Claude) | ✅ Зафиксировано |

**Решение:** LangChain + LangGraph для AI workflows. **НЕ МЕНЯТЬ**.

**Архитектурные решения:**
- Все AI процессы реализуются через LangGraph workflows
- Агенты — stateless компоненты
- Состояние хранится в PostgreSQL
- LangGraph state — только внутри workflow

---

## Структура API

### RESTful API Design

**Базовый префикс:** `/api/v1`

**Структура endpoints:**

```
/api/v1/
├── auth/                    # Аутентификация
│   ├── POST /register       # Регистрация
│   ├── POST /login          # Вход
│   ├── POST /logout         # Выход
│   └── POST /refresh        # Обновление токена
│
├── users/                   # Пользователи
│   ├── GET /users/me        # Текущий пользователь
│   └── PATCH /users/me      # Обновление профиля
│
├── shops/                   # Магазины
│   ├── GET /shops           # Список магазинов
│   ├── POST /shops          # Создать магазин
│   ├── GET /shops/{id}      # Получить магазин
│   └── PATCH /shops/{id}    # Обновить магазин
│
├── products/                # Товары
│   ├── GET /products        # Список товаров
│   ├── POST /products       # Создать товар
│   ├── GET /products/{id}   # Получить товар
│   ├── PATCH /products/{id} # Обновить товар
│   └── DELETE /products/{id}# Удалить товар
│
├── sales/                   # Продажи
│   ├── GET /sales           # Список продаж
│   ├── GET /sales/stats     # Статистика продаж
│   └── GET /sales/analytics # Аналитика продаж
│
├── reviews/                 # Отзывы
│   ├── GET /reviews         # Список отзывов
│   ├── GET /reviews/{id}    # Получить отзыв
│   ├── POST /reviews/{id}/reply  # Ответить на отзыв
│   └── GET /reviews/sentiment    # Анализ тональности
│
├── inventory/               # Остатки
│   ├── GET /inventory       # Список остатков
│   ├── GET /inventory/alerts# Алерты по остаткам
│   └── GET /inventory/forecast   # Прогноз остатков
│
├── content/                 # Контент
│   ├── POST /content/generate-description  # Генерация описания
│   ├── POST /content/generate-images       # Генерация изображений
│   ├── POST /content/generate-video        # Генерация видео
│   └── POST /content/optimize-seo          # SEO оптимизация
│
├── pricing/                 # Ценообразование
│   ├── GET /pricing/analyze # Анализ цен конкурентов
│   ├── POST /pricing/recommend  # Рекомендации по ценам
│   └── PATCH /pricing/update    # Обновление цен
│
├── workflows/               # AI Workflows
│   ├── POST /workflows/analyze-sales       # Анализ продаж
│   ├── POST /workflows/create-product      # Создание карточки
│   ├── POST /workflows/process-review      # Обработка отзыва
│   └── GET /workflows/{id}/status          # Статус workflow
│
└── tasks/                   # Задачи
    ├── GET /tasks           # Список задач
    ├── GET /tasks/{id}      # Статус задачи
    └── DELETE /tasks/{id}   # Отменить задачу
```

**Стандарты API:**
- REST принципы
- JSON формат данных
- HTTP статус коды (200, 201, 400, 401, 403, 404, 500)
- Пагинация: `?page=1&limit=20`
- Фильтрация: `?filter[status]=active`
- Сортировка: `?sort=-created_at`
- Валидация через Pydantic
- Автоматическая документация через OpenAPI

---

## HTTP Client

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **HTTPX** | 0.26.0 | Requests, aiohttp | Async/sync support, HTTP/2, совместимость с Requests API | ✅ Зафиксировано |
| **aiohttp** | 3.9.1 | - | Дополнительный async HTTP клиент для специфичных случаев | ✅ Зафиксировано |

**Решение:** HTTPX для всех внешних API запросов. **НЕ МЕНЯТЬ**.

---

## Configuration & Settings

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **Pydantic** | 2.6.0 | Marshmallow, attrs | Валидация данных, type hints, автоматическая документация | ✅ Зафиксировано |
| **Pydantic-settings** | 2.1.0 | python-decouple, environs | Управление настройками через env переменные | ✅ Зафиксировано |
| **python-dotenv** | 1.0.0 | - | Загрузка .env файлов | ✅ Зафиксировано |

**Решение:** Pydantic Settings — управление конфигурацией. **НЕ МЕНЯТЬ**.

**Архитектура конфигурации:**
- Все настройки в `backend/config/settings.py`
- Загрузка из environment variables
- Поддержка .env файлов
- Валидация при запуске приложения
- Singleton паттерн для settings

---

## Security & Authentication

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **python-jose[cryptography]** | 3.3.0 | PyJWT | JWT токены, поддержка различных алгоритмов | ✅ Зафиксировано |
| **passlib[bcrypt]** | 1.7.4 | argon2-cffi | Хеширование паролей, bcrypt алгоритм | ✅ Зафиксировано |

**Решение:** JWT токены + bcrypt для паролей. **НЕ МЕНЯТЬ**.

**Архитектура безопасности:**
- JWT access tokens (срок жизни: 60 минут)
- JWT refresh tokens (срок жизни: 7 дней)
- Bcrypt для хеширования паролей
- OAuth2 Password Bearer scheme

---

## Data Processing

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **Pandas** | 2.2.0 | Polars | Стандарт для анализа данных, богатая экосистема | ✅ Зафиксировано |
| **NumPy** | 1.26.3 | - | Математические операции, поддержка массивов | ✅ Зафиксировано |

**Решение:** Pandas + NumPy для анализа данных. **НЕ МЕНЯТЬ**.

---

## Logging

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **structlog** | 24.1.0 | loguru, python-json-logger | Структурированное логирование, JSON формат | ✅ Зафиксировано |

**Решение:** Structlog для продакшена, стандартный logging для разработки. **НЕ МЕНЯТЬ**.

**Архитектура логирования:**
- Уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console handler (development)
- Rotating file handler (production, 10MB, 5 backups)
- Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

---

## Testing

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **pytest** | 7.4.4 | unittest, nose2 | Современный testing framework, fixtures, plugins | ✅ Зафиксировано |
| **pytest-asyncio** | 0.23.3 | - | Поддержка async тестов | ✅ Зафиксировано |
| **pytest-cov** | 4.1.0 | coverage.py | Code coverage reporting | ✅ Зафиксировано |

**Решение:** Pytest для всех тестов. **НЕ МЕНЯТЬ**.

---

## Code Quality

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **Black** | 24.1.1 | autopep8, yapf | Opinionated formatter, стандарт в Python community | ✅ Зафиксировано |
| **Flake8** | 7.0.0 | pylint, pycodestyle | Linting, проверка PEP 8 | ✅ Зафиксировано |
| **MyPy** | 1.8.0 | pyright, pyre | Type checking, проверка type hints | ✅ Зафиксировано |

**Решение:** Black + Flake8 + MyPy для качества кода. **НЕ МЕНЯТЬ**.

**Настройки:**
- Line length: 88 (Black default)
- Type hints обязательны для всех функций
- Docstrings для всех публичных методов

---

## Frontend Stack (Desktop App)

### Framework

| Библиотека | Версия | Альтернативы | Причина выбора | Статус |
|------------|--------|--------------|----------------|--------|
| **Electron** | 24.14.0 | Tauri, NW.js | Зрелое решение, богатая экосистема, кросс-платформенность | ✅ Зафиксировано |
| **React** | 19.2.0 | Vue, Svelte | Популярность, экосистема, React Hooks | ✅ Зафиксировано |
| **Vite** | 8.0.3 | Webpack, Parcel | Быстрая разработка и сборка renderer части Electron | ✅ Зафиксировано |

---

## Vector Database (Future)

| База данных | Версия | Альтернативы | Причина выбора | Статус |
|-------------|--------|--------------|----------------|--------|
| **Qdrant** | TBD | Pinecone, Weaviate, ChromaDB | Open-source, высокая производительность, Rust | 🔜 Планируется (Этап 8+) |

**Назначение:** Хранение контекста AI, истории решений, knowledge base

---

## External APIs

### Wildberries API

**Базовый URL:** `https://suppliers-api.wildberries.ru`

**Документация:** https://openapi.wildberries.ru/

**Основные endpoints:**
- `/api/v3/stocks` — остатки
- `/api/v1/supplier/sales` — продажи
- `/api/v1/feedbacks` — отзывы
- `/content/v1/cards` — карточки товаров

**Статус:** 🔜 Этап 2

---

## Архитектурные паттерны

### Backend Architecture Patterns

| Паттерн | Описание | Статус |
|---------|----------|--------|
| **Repository Pattern** | Абстракция работы с БД | ✅ Будет использоваться |
| **Service Layer** | Бизнес-логика в сервисах | ✅ Используется (health_service) |
| **Dependency Injection** | FastAPI dependencies | ✅ Используется (dependencies.py) |
| **Factory Pattern** | Создание агентов и workflow | ✅ Будет использоваться |
| **Strategy Pattern** | Различные AI стратегии | ✅ Будет использоваться |
| **Application Factory** | create_app() pattern | ✅ Используется (main.py) |
| **Base Model Pattern** | Общий Base класс для моделей | ✅ Используется (database/base.py) |

### API Design Patterns

| Паттерн | Описание | Статус |
|---------|----------|--------|
| **RESTful API** | REST принципы | ✅ Используется |
| **Request/Response DTO** | Pydantic models | ✅ Используется |
| **Error Handling** | Централизованная обработка ошибок | ✅ Будет использоваться |
| **Pagination** | Cursor-based pagination | ✅ Будет использоваться |
| **Filtering** | Query parameters | ✅ Будет использоваться |

---

## Версионирование

### API Versioning

**Стратегия:** URL-based versioning

**Формат:** `/api/v{major}/`

**Текущая версия:** v1

**Правила:**
- Major version в URL (`/api/v1/`, `/api/v2/`)
- Breaking changes требуют новой версии
- Поддержка старых версий минимум 6 месяцев

### Database Migrations

**Инструмент:** Alembic

**Команды:**
```bash
# Создать миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

---

## CI/CD (Future)

| Инструмент | Назначение | Статус |
|------------|------------|--------|
| **GitHub Actions** | CI/CD pipeline | 🔜 Планируется |
| **Docker** | Контейнеризация | 🔜 Планируется |
| **Docker Compose** | Локальная разработка | ✅ Используется |

---

## Мониторинг и Observability (Future)

| Инструмент | Назначение | Статус |
|------------|------------|--------|
| **Sentry** | Error tracking | 🔜 Планируется |
| **Prometheus** | Метрики | 🔜 Планируется |
| **Grafana** | Визуализация метрик | 🔜 Планируется |

---

## Ключевые модули (реализовано)

### Dependency Container (config/dependencies.py)

Централизованное управление зависимостями:

```python
# Database dependencies
get_db() -> Session                   # Sync DB session
get_async_db() -> AsyncSession        # Async DB session

# Redis dependencies  
get_redis() -> Redis                  # Sync Redis
get_async_redis() -> AsyncRedis       # Async Redis

# Configuration
get_settings() -> Settings            # App settings
```

**Статус:** ✅ Реализовано

---

### Base Database Model (database/base.py)

Базовая модель для всех таблиц:

```python
class Base(DeclarativeBase):
    id: Mapped[int]                   # Primary key
    created_at: Mapped[datetime]      # Auto timestamp
    updated_at: Mapped[datetime]      # Auto timestamp
```

**Использование:**
```python
class Product(Base):
    __tablename__ = "products"
    name: Mapped[str]
    # id, created_at, updated_at наследуются автоматически
```

**Статус:** ✅ Реализовано

---

### Health Check Service (services/health_service.py)

Сервис проверки состояния системы:

```python
class HealthService:
    async def check_database() -> str
    async def check_redis() -> str
    async def get_health_status() -> HealthStatus
```

**Статус:** ✅ Реализовано

---

### Versioned API (api/v1.py)

API версионирование:

```python
router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/")           # /api/v1/
@router.get("/health")     # /api/v1/health
```

**Статус:** ✅ Реализовано

---

## Правила изменения стека

### ✅ Можно менять:

- Patch версии библиотек (bug fixes)
- Добавление новых библиотек (если не конфликтуют)
- Настройки конфигурации

### ⚠️ Требует обсуждения:

- Minor версии библиотек
- Добавление альтернативных решений
- Изменение архитектурных паттернов

### ❌ ЗАПРЕЩЕНО менять без веской причины:

- Major версии библиотек
- Основной стек (FastAPI, SQLAlchemy, LangChain)
- ORM решение
- Структура API
- База данных

### Процесс изменения:

1. Создать issue с обоснованием
2. Провести оценку рисков
3. Проверить обратную совместимость
4. Обновить TECH_STACK.md
5. Обновить документацию
6. Создать миграционный план

---

## История изменений

| Дата | Изменение | Причина | Версия |
|------|-----------|---------|--------|
| 2026-03-09 | Инициализация TECH_STACK.md | Фиксация технологических решений Этапа 1 | 0.1.0 |
| 2026-03-09 | Архитектурные улучшения | Добавлены: versioned API, base model, dependencies, health service | 0.1.1 |
| 2026-03-11 | Этап 2: Интеграция с Wildberries API | Mock API, WildberriesService, Pydantic схемы, API endpoints | 0.2.0 |
| 2026-03-12 | Этап 3: Модель данных системы | SQLAlchemy модели, Alembic, Repository Pattern, Data Sync Service, Рефакторинг WB services и schemas | 0.3.0 |
| 2026-03-12 | Этап 4: Task System и Scheduler | Celery + Redis (task queue), Celery Beat (scheduler), TaskService, Tasks API, Flower monitoring, Периодические задачи синхронизации | 0.4.0 |
| 2026-03-12 | Этап 4: Критические исправления | SingletonTask (concurrency), TaskExecution (metrics), Autoretry + exponential backoff, Chunking, Workflow integration, Event-driven triggers | 0.4.1 |
| 2026-03-12 | Этап 5: Orchestrator | Orchestrator для управления workflows, WorkflowRegistry, BaseWorkflow, CheckInventoryWorkflow (LangGraph), Интеграция с EventListener, Workflows API | 0.5.0 |
| 2026-03-28 | Этап 6: Базовая система агентов | Реализованы stateless агенты analytics/inventory/review/content/pricing | 0.6.0 |
| 2026-03-28 | Этап 7: AI Workflows (LangGraph) | Добавлены доменные workflow sales/product/review/pricing/inventory | 0.7.0 |
| 2026-03-28 | Этап 8: AI сервисы | Добавлен ai_service (DeepSeek/OpenAI/Anthropic), AI endpoints, интеграция в workflows | 0.8.0 |
| 2026-03-28 | Этап 9: Action Layer | Добавлен action_service, action endpoints, execute_action в workflows | 0.9.0 |
| 2026-03-28 | Этап 10: Desktop приложение | Добавлен desktop-app (Electron + React + Vite) с разделами Dashboard/Products/Reviews/Content AI/Inventory/Settings | 0.10.0 |

---

## Проверка совместимости

Перед обновлением библиотек проверить:

1. **Breaking changes** в changelog
2. **Deprecation warnings** в текущей версии
3. **Обратную совместимость** с существующим кодом
4. **Зависимости** других библиотек
5. **Тесты** — все должны проходить

---

## Контакты и ресурсы

### Документация:
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- LangChain: https://python.langchain.com/
- LangGraph: https://langchain-ai.github.io/langgraph/

### Community:
- Python Discord: https://discord.gg/python
- FastAPI Discord: https://discord.gg/fastapi

---

**Последнее обновление:** 9 марта 2026  
**Версия документа:** 1.0  
**Статус:** ✅ Актуально
