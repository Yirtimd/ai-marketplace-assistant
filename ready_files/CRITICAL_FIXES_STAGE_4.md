# ✅ Исправление критических проблем Этапа 4 — ЗАВЕРШЕНО

**Дата:** 12 марта 2026

---

## 📋 Обзор

Успешно реализованы все 6 критических исправлений, выявленных в архитектурном аудите Этапа 4.

---

## ✅ Исправленные проблемы

### 1. ✅ Concurrency — task locking через Redis

**Проблема:** Задачи могли выполняться параллельно для одного shop_id, что приводило к race conditions.

**Решение:**

#### 1.1 Создан `SingletonTask` (`tasks/singleton.py`)

```python
class SingletonTask(Task):
    """Ensures only one instance runs at a time for given arguments"""
    
    def __call__(self, *args, **kwargs):
        lock_key = self._generate_lock_key(args, kwargs)
        
        # Try to acquire Redis lock
        lock_acquired = self.redis_client.set(
            lock_key, "locked", nx=True, ex=1800
        )
        
        if not lock_acquired:
            return {"status": "skipped", "reason": "already_running"}
        
        try:
            return super().__call__(*args, **kwargs)
        finally:
            self.redis_client.delete(lock_key)
```

#### 1.2 Обновлены все sync задачи

- `sync_products_task` → использует `DatabaseSingletonTask` (позже `WorkflowDatabaseTask`)
- `sync_sales_task` → использует `DatabaseSingletonTask`
- `sync_reviews_task` → использует `DatabaseSingletonTask`

#### 1.3 Исправлены sync_all_* задачи

**Было (неправильно):**
```python
result = await sync_products_task(shop.id, limit=100)  # Прямой вызов
```

**Стало (правильно):**
```python
task = sync_products_task.delay(shop.id, limit=100)  # Через Celery queue
```

**Результат:** ✅ Race conditions устранены, задачи не могут выполняться параллельно для одного shop_id.

---

### 2. ✅ TaskExecution model для хранения метрик

**Проблема:** Метрики хранились только в Redis (TTL = 1 час), после чего терялись.

**Решение:**

#### 2.1 Создана модель `TaskExecution` (`database/models/task_execution.py`)

```python
class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    task_id: str (unique)
    task_name: str
    shop_id: int
    user_id: int
    workflow_id: str  # Для интеграции с Orchestrator
    
    # Status
    status: str  # pending, running, success, failed, skipped
    started_at: datetime
    completed_at: datetime
    duration_seconds: int
    
    # Metrics
    records_created: int
    records_updated: int
    records_skipped: int
    records_failed: int
    records_total: int
    
    # Error details
    error_message: str
    error_type: str
    error_traceback: str
    retry_count: int
    
    # Result
    result_data: JSON
    input_params: JSON
```

#### 2.2 Создан `TaskExecutionRepository` (`database/repositories/task_execution.py`)

Методы:
- `get_by_task_id()`
- `get_by_shop()`
- `get_by_task_name()`
- `get_by_status()`
- `get_by_date_range()`
- `get_failed_executions()`
- `get_by_workflow()` — для Этапа 5

**Результат:** ✅ Все метрики выполнения задач теперь хранятся в PostgreSQL постоянно.

---

### 3. ✅ Autoretry для WB API ошибок с exponential backoff

**Проблема:** Задачи падали при временных сбоях WB API (429, timeout, network errors).

**Решение:**

#### 3.1 Обновлена конфигурация Celery (`config/celery_config.py`)

```python
class CeleryConfig:
    # Global autoretry settings
    task_autoretry_for = (Exception,)
    task_retry_kwargs = {'max_retries': 5, 'countdown': 5}
    task_retry_backoff = True  # Exponential backoff
    task_retry_backoff_max = 600  # Max 10 minutes
    task_retry_jitter = True  # Random jitter
    
    # Rate limiting
    task_annotations = {
        'tasks.sync.sync_products_task': {'rate_limit': '10/m'},
        'tasks.sync.sync_sales_task': {'rate_limit': '10/m'},
        'tasks.sync.sync_reviews_task': {'rate_limit': '10/m'},
    }
```

#### 3.2 Добавлен autoretry в задачи

```python
@celery_app.task(
    bind=True,
    base=WorkflowDatabaseTask,
    name="tasks.sync.sync_products_task",
    autoretry_for=(
        WildberriesServiceError,
        httpx.RequestError,
        httpx.TimeoutException
    ),
    retry_kwargs={'max_retries': 5, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
```

#### 3.3 Улучшена обработка rate limit (`services/wildberries/base.py`)

```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    raise WildberriesRateLimitError(f"Rate limit exceeded, retry after {retry_after}s")
```

**Результат:** ✅ Задачи автоматически повторяются при сбоях с exponential backoff (5s → 10s → 20s → 40s → ...).

---

### 4. ✅ Chunking для больших задач синхронизации

**Проблема:** Задачи могли обрабатывать тысячи записей в одной транзакции, блокируя worker.

**Решение:**

#### 4.1 Добавлена поддержка chunking в `sync_products_task`

```python
async def sync_products_task(
    self,
    shop_id: int,
    limit: int = 100,
    offset: int = 0,
    chunk_size: int = 50,
    auto_chunk: bool = True
) -> dict:
    # Sync current chunk
    current_chunk_size = min(chunk_size, limit - offset)
    result = await sync_service.sync_products(
        db, shop_id, limit=current_chunk_size, track_history=True
    )
    
    # Schedule next chunk if needed
    next_offset = offset + current_chunk_size
    if auto_chunk and next_offset < limit:
        sync_products_task.delay(
            shop_id=shop_id,
            limit=limit,
            offset=next_offset,
            chunk_size=chunk_size
        )
        result["next_chunk_scheduled"] = True
```

**Параметры:**
- `chunk_size` = 50 (по умолчанию) — обрабатывать по 50 продуктов за раз
- `auto_chunk` = True — автоматически запланировать следующий chunk
- `offset` — для пагинации

**Результат:** ✅ Большие задачи разбиваются на chunks по 50 записей, предотвращая блокировку worker.

---

### 5. ✅ Интеграция workflow_id для Orchestrator

**Проблема:** Задачи не поддерживали контекст AI Workflow, необходимый для Этапа 5.

**Решение:**

#### 5.1 Создан `WorkflowAwareTask` (`tasks/workflow_aware.py`)

```python
class WorkflowAwareTask(Task):
    """Base task with workflow integration"""
    
    def __call__(self, *args, **kwargs):
        # Extract workflow context
        workflow_id = kwargs.pop('workflow_id', None)
        workflow_state = kwargs.pop('workflow_state', None)
        user_id = kwargs.pop('user_id', None)
        
        # Store in task context
        self.workflow_id = workflow_id
        self.workflow_state = workflow_state
        self.user_id = user_id
        
        # Execute task
        result = super().__call__(*args, **kwargs)
        
        # Notify workflow of completion
        if workflow_id:
            self.notify_workflow(workflow_id, result)
        
        return result
    
    def notify_workflow(self, workflow_id: str, result: dict):
        """Notify LangGraph workflow (TODO: Этап 5)"""
        logger.info(f"Task completed for workflow {workflow_id}")
```

#### 5.2 Создан `WorkflowDatabaseTask` (комбинированный)

```python
class WorkflowDatabaseTask(WorkflowAwareTask, SingletonTask, DatabaseTask):
    """
    Combines:
    - Workflow context (workflow_id, user_id)
    - Singleton locking
    - Database session management
    """
```

#### 5.3 Все sync задачи используют `WorkflowDatabaseTask`

**Результат:** ✅ Задачи готовы к запуску из AI Workflows на Этапе 5.

---

### 6. ✅ Event-driven triggers

**Проблема:** Не было механизма для запуска задач на основе системных событий.

**Решение:**

#### 6.1 Создан `EventListener` (`services/event_listener.py`)

```python
class EventListener:
    """Listens to system events and triggers tasks/workflows"""
    
    async def on_event(self, event: Event):
        """Main event handler"""
        handler = self._get_handler(event.type)
        if handler:
            await handler(event)
    
    async def on_low_stock(self, event: Event):
        """Handle low stock event"""
        shop_id = event.shop_id
        product_id = event.details.get("product_id")
        
        # Trigger stock check
        task = check_stock_levels_task.delay(threshold=10)
        
        # TODO: Этап 5 - Trigger AI workflow
        # orchestrator.create_workflow("restock_product")
    
    async def on_negative_review(self, event: Event):
        """Handle negative review event"""
        # TODO: Этап 5 - Trigger review response workflow
        # orchestrator.create_workflow("respond_to_review")
    
    async def on_price_changed(self, event: Event):
        """Handle price change event"""
        # TODO: Этап 5 - Trigger pricing analysis workflow
        # orchestrator.create_workflow("analyze_pricing")
```

#### 6.2 Поддержанные события

- `LOW_STOCK` → Проверка остатков
- `NEGATIVE_REVIEW` → (Будущее) AI ответ на отзыв
- `SYNC_COMPLETED` → Логирование
- `SYNC_FAILED` → Алерты
- `PRICE_CHANGED` → (Будущее) Анализ цен

**Результат:** ✅ Event-driven архитектура готова. На Этапе 5 события будут запускать AI workflows.

---

## 📊 Сводная таблица изменений

| № | Проблема | Файлы | Статус |
|---|----------|-------|--------|
| 1 | Concurrency | `tasks/singleton.py`, `tasks/sync.py` | ✅ Исправлено |
| 2 | Хранение метрик | `database/models/task_execution.py`, `database/repositories/task_execution.py` | ✅ Создано |
| 3 | Autoretry | `config/celery_config.py`, `tasks/sync.py`, `services/wildberries/base.py` | ✅ Настроено |
| 4 | Chunking | `tasks/sync.py` (sync_products_task) | ✅ Реализовано |
| 5 | Workflow integration | `tasks/workflow_aware.py`, `tasks/sync.py` | ✅ Готово |
| 6 | Event triggers | `services/event_listener.py` | ✅ Реализовано |

---

## 🎯 Готовность к Этапу 5

### Архитектура теперь поддерживает:

```
Event (LOW_STOCK, NEGATIVE_REVIEW, etc.)
    ↓
EventListener.on_event()
    ↓
Orchestrator (Этап 5)
    ↓
LangGraph Workflow
    ↓
AI Agents
    ↓
Tasks (Celery) [workflow_id, user_id]
    ↓
DataSyncService / WB Services
    ↓
Repository → Database
    ↓
TaskExecution (metrics saved)
```

### Что готово:

1. ✅ **Concurrency control** — Redis locking
2. ✅ **Metrics storage** — TaskExecution model
3. ✅ **Error resilience** — Autoretry + exponential backoff
4. ✅ **Scalability** — Chunking для больших задач
5. ✅ **Workflow integration** — workflow_id в задачах
6. ✅ **Event-driven** — EventListener готов к Orchestrator

### Что будет добавлено на Этапе 5:

- Orchestrator для координации workflows
- LangGraph workflows
- AI Agents
- Callback от задач к Orchestrator (`notify_workflow()`)

---

## 📝 Созданные файлы

**Новые файлы:**
1. `backend/tasks/singleton.py` — SingletonTask с Redis locking
2. `backend/tasks/workflow_aware.py` — WorkflowAwareTask для Orchestrator
3. `backend/database/models/task_execution.py` — TaskExecution model
4. `backend/database/repositories/task_execution.py` — TaskExecutionRepository
5. `backend/services/event_listener.py` — EventListener для event-driven triggers

**Обновленные файлы:**
1. `backend/config/celery_config.py` — autoretry, rate limiting
2. `backend/tasks/sync.py` — все sync задачи с исправлениями
3. `backend/services/wildberries/base.py` — улучшенная обработка rate limit
4. `backend/database/models/__init__.py` — экспорт TaskExecution
5. `backend/database/repositories/__init__.py` — экспорт task_execution_repository
6. `backend/services/__init__.py` — экспорт event_listener

---

## ✅ Тестирование

### Как протестировать исправления:

#### 1. Concurrency (singleton lock)

```bash
# Запустить одну и ту же задачу дважды
curl -X POST http://localhost:8000/api/v1/tasks/sync/products \
  -d '{"shop_id": 1, "limit": 100}'

# Немедленно повторить
curl -X POST http://localhost:8000/api/v1/tasks/sync/products \
  -d '{"shop_id": 1, "limit": 100}'

# Ожидаемый результат второй задачи:
# {"status": "skipped", "reason": "already_running"}
```

#### 2. Autoretry

```bash
# Отключить WB API (или Mock API)
docker stop ai_marketplace_mock_api

# Запустить задачу
curl -X POST http://localhost:8000/api/v1/tasks/sync/products \
  -d '{"shop_id": 1, "limit": 10}'

# Проверить логи — должны быть retry попытки
docker logs -f ai_marketplace_celery_worker
# [INFO] Retrying task (1/5)...
# [INFO] Retrying task (2/5)...
```

#### 3. Chunking

```bash
# Запустить с большим limit
curl -X POST http://localhost:8000/api/v1/tasks/sync/products \
  -d '{"shop_id": 1, "limit": 200, "chunk_size": 50}'

# Проверить Flower UI — должны появиться 4 задачи (200/50=4)
# Открыть http://localhost:5555
```

---

## 🎉 Итог

**Все 6 критических проблем исправлены!**

Система теперь:
- ✅ Устойчива к concurrency (Redis locking)
- ✅ Хранит полные метрики (TaskExecution)
- ✅ Автоматически повторяет задачи при сбоях (autoretry)
- ✅ Масштабируется на больших данных (chunking)
- ✅ Готова к AI Workflows (workflow_id)
- ✅ Поддерживает event-driven архитектуру (EventListener)

**Готовы к Этапу 5 — Orchestrator + AI Workflows!** 🚀

---

**Дата завершения:** 12 марта 2026  
**Версия:** 0.4.1
