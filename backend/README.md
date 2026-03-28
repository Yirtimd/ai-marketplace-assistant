# AI Marketplace Assistant - Backend

Серверная часть AI Marketplace Assistant - AI-платформы для автоматизации работы продавцов на маркетплейсах.

## Архитектура

Backend построен на модульной архитектуре со следующими компонентами:

```
backend/
├── api/            # HTTP endpoints
├── orchestrator/   # Запуск AI workflows
├── agents/         # AI агенты
├── workflows/      # LangGraph workflows
├── services/       # Внешние API сервисы
├── tasks/          # Фоновые задачи
├── database/       # Модели и подключение к БД
└── config/         # Конфигурация приложения
```

## Технологии

- **Web Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **AI Framework**: LangChain + LangGraph
- **Python**: 3.11+

## Установка

1. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:

```bash
cp .env.example .env
# Отредактируйте .env и укажите свои значения
```

4. Запустите PostgreSQL и Redis:

```bash
# Используя Docker Compose (рекомендуется)
docker-compose up -d postgres redis

# Или установите локально
```

## Запуск

### Режим разработки

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Режим production

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Документация

После запуска сервера доступна автоматическая документация:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `GET /` - Информация о приложении (deprecated, используйте /api/v1/)
- `GET /api/v1/` - API v1 root
- `GET /api/v1/health` - Health check

## Разработка

Следуйте правилам из документации:

- `ARCHITECTURE.md` - Архитектура системы
- `PROJECT_RULES.md` - Правила разработки
- `DEVELOPMENT_WORKFLOW.md` - Процесс разработки
- `ROADMAP.md` - План разработки

## Этап разработки

Текущий этап: **Этап 9 - Action Layer**

Реализовано:
- ✅ Базовая инфраструктура backend
- ✅ Интеграция Wildberries API и data sync
- ✅ Модель данных и репозитории
- ✅ Task system на Celery
- ✅ Orchestrator + WorkflowRegistry + LangGraph workflow
- ✅ Базовая система stateless агентов (`agents/`)
- ✅ Набор доменных workflow (sales, content, review, pricing, inventory)
- ✅ AI Service слой (`services/ai_service.py`) с DeepSeek/OpenAI/Anthropic
- ✅ AI endpoints (`/api/v1/ai/*`) для ручного тестирования
- ✅ Action Layer (`services/action_service.py`)
- ✅ Action API endpoints (`/api/v1/actions/*`)
- ✅ Выполнение действий из workflow через `execute_action`

Следующий этап: **Этап 10 - Desktop приложение**

## Лицензия

Proprietary
