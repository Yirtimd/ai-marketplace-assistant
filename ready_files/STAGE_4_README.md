# Этап 4: Task System и Scheduler - README

## Обзор

Этап 4 добавляет в проект полноценную систему фоновых задач на базе **Celery** с поддержкой периодических задач, мониторинга и API управления.

---

## Что добавлено

### 1. Celery Infrastructure

**Конфигурация:** `config/celery_config.py`
- Redis как broker и result backend
- Настройки таймаутов и ограничений
- Beat schedule для периодических задач

**Приложение:** `celery_app.py`
- Инициализация Celery
- Автоматическое обнаружение задач

### 2. Tasks (Задачи)

**Sync Tasks** (`tasks/sync.py`):
- Синхронизация продуктов, продаж, отзывов
- Поддержка как отдельных магазинов, так и пакетной синхронизации
- Интеграция с DataSyncService (Этап 3)

**Monitoring Tasks** (`tasks/monitoring.py`):
- Проверка уровня остатков товаров
- Low stock alerts

**Analytics Placeholder** (`tasks/analytics.py`):
- Заглушка для будущих AI аналитических задач

### 3. TaskService

**Service Layer** (`services/task_service.py`):
- Управление жизненным циклом задач
- Создание, мониторинг, отмена задач
- Получение списков активных и запланированных задач

### 4. Tasks API

**Endpoints** (`api/routes/tasks.py`):
- `POST /api/v1/tasks/sync/products` — запуск синхронизации продуктов
- `POST /api/v1/tasks/sync/sales` — запуск синхронизации продаж
- `POST /api/v1/tasks/sync/reviews` — запуск синхронизации отзывов
- `GET /api/v1/tasks/{task_id}` — статус задачи
- `DELETE /api/v1/tasks/{task_id}` — отмена задачи
- `GET /api/v1/tasks/` — список всех задач

### 5. Docker Integration

**Сервисы** (`docker-compose.yml`):
- `celery_worker` — обработка задач
- `celery_beat` — периодический планировщик
- `flower` — веб-интерфейс мониторинга (порт 5555)

### 6. Shell Scripts

**Скрипты** (`scripts/`):
- `start_celery_worker.sh` — запуск worker
- `start_celery_beat.sh` — запуск beat scheduler

---

## Архитектура

```
API Request → TaskService → Celery Queue (Redis)
                               ↓
                         Celery Worker
                               ↓
                         Task Execution
                               ↓
                    DataSyncService (Этап 3)
                               ↓
                      WB Services (Этап 2)
                               ↓
                   Repository → Database (Этап 3)
```

---

## Периодические задачи

Celery Beat автоматически запускает:

| Задача | Интервал | Описание |
|--------|----------|----------|
| sync_all_products_task | 6 часов | Синхронизация продуктов всех магазинов |
| sync_all_sales_task | 1 час | Синхронизация продаж всех магазинов |
| sync_all_reviews_task | 2 часа | Синхронизация отзывов всех магазинов |
| check_stock_levels_task | 30 минут | Проверка остатков, low stock alerts |

---

## Запуск

### Вариант 1: Docker (рекомендуется)

```bash
cd backend
docker-compose up -d
```

**Проверка:**
```bash
docker ps
```

**Flower UI:**
```
http://localhost:5555
```

### Вариант 2: Локально

**Терминал 1 — Worker:**
```bash
cd backend
./scripts/start_celery_worker.sh
```

**Терминал 2 — Beat:**
```bash
cd backend
./scripts/start_celery_beat.sh
```

---

## Тестирование

**Запустить задачу:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks/sync/products \
  -H "Content-Type: application/json" \
  -d '{"shop_id": 1, "limit": 100}'
```

**Проверить статус:**
```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

**Flower UI:**
- Откройте `http://localhost:5555`
- Просмотр активных задач, истории выполнения, метрик

---

## Логи

**Docker:**
```bash
docker logs -f ai_marketplace_celery_worker
docker logs -f ai_marketplace_celery_beat
```

**Локальный:**
```bash
tail -f backend/logs/celery_worker.log
tail -f backend/logs/celery_beat.log
```

---

## Зависимости

Добавлены в `requirements.txt`:
```
celery[redis]==5.3.4
redis==5.0.1
flower==2.0.1
```

---

## Документация

- `ready_files/ЭТАП_4_ЗАВЕРШЕН.md` — полный отчет
- `ready_files/TESTING_STAGE_4.md` — руководство по тестированию
- `ready_files/STAGE_4_SUMMARY.md` — краткий summary

---

## Готовность к Этапу 5

✅ Task System полностью готов  
✅ Периодические задачи работают  
✅ API для управления задачами реализован  
✅ Мониторинг через Flower доступен  
✅ Интеграция с Этапами 2 и 3 завершена  

**Следующий этап:** Orchestrator (координация AI workflows)
