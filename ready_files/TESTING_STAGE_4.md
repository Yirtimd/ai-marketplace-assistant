# Быстрое руководство: Тестирование Этапа 4

## Цель

Проверить работу Task System (Celery + Redis).

---

## Шаг 1: Запуск всех сервисов

### Вариант A: Docker (рекомендуется)

```bash
cd backend
docker-compose up -d
```

**Проверка запуска:**

```bash
docker ps
```

Должны быть запущены:
- `ai_marketplace_postgres`
- `ai_marketplace_redis`
- `ai_marketplace_celery_worker`
- `ai_marketplace_celery_beat`
- `ai_marketplace_flower`

### Вариант B: Локальный запуск

**Терминал 1 — Redis:**

```bash
redis-server
```

**Терминал 2 — PostgreSQL:**

```bash
# Если установлен локально
pg_ctl -D /usr/local/var/postgres start
```

**Терминал 3 — Celery Worker:**

```bash
cd backend
./scripts/start_celery_worker.sh
```

**Терминал 4 — Celery Beat:**

```bash
cd backend
./scripts/start_celery_beat.sh
```

---

## Шаг 2: Открыть Flower UI

**URL:** http://localhost:5555

Flower — это веб-интерфейс для мониторинга Celery задач.

**Проверка:**
- Должны отображаться активные workers
- Список периодических задач (Celery Beat)

---

## Шаг 3: Тестирование через API

### 3.1 Запустить задачу синхронизации продуктов

```bash
curl -X POST http://localhost:8000/api/v1/tasks/sync/products \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 1,
    "limit": 100
  }'
```

**Ответ (пример):**

```json
{
  "task_id": "abc123-def456-...",
  "task_name": "tasks.sync.sync_products_task",
  "status": "pending",
  "created_at": "2026-03-12T12:00:00"
}
```

**Скопируйте `task_id` для следующего шага.**

---

### 3.2 Проверить статус задачи

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

**Замените `{task_id}` на скопированный ID.**

**Ответ (пример):**

```json
{
  "task_id": "abc123-def456-...",
  "status": "COMPLETED",
  "state": "SUCCESS",
  "result": {
    "created": 5,
    "updated": 10,
    "skipped": 2,
    "total": 17
  }
}
```

**Возможные статусы:**
- `PENDING` — задача в очереди
- `IN_PROGRESS` — задача выполняется
- `COMPLETED` — задача завершена успешно
- `FAILED` — задача завершилась с ошибкой

---

### 3.3 Список всех задач

```bash
curl http://localhost:8000/api/v1/tasks/
```

**Ответ:**

```json
{
  "active": [
    {
      "task_id": "...",
      "task_name": "tasks.sync.sync_sales_task",
      "worker": "celery@worker1"
    }
  ],
  "scheduled": [
    {
      "task_id": "...",
      "task_name": "tasks.sync.sync_products_task",
      "eta": "2026-03-12T13:00:00"
    }
  ],
  "total_active": 1,
  "total_scheduled": 3
}
```

---

### 3.4 Отменить задачу

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/{task_id}?terminate=false
```

**Ответ:**

```json
{
  "task_id": "abc123-...",
  "status": "cancelled",
  "terminated": false
}
```

---

## Шаг 4: Проверка логов

### Docker:

**Celery Worker:**

```bash
docker logs -f ai_marketplace_celery_worker
```

**Celery Beat:**

```bash
docker logs -f ai_marketplace_celery_beat
```

### Локальный запуск:

Логи записываются в файлы:
- `backend/logs/celery_worker.log`
- `backend/logs/celery_beat.log`

```bash
tail -f backend/logs/celery_worker.log
```

---

## Шаг 5: Проверка периодических задач

Celery Beat запускает задачи по расписанию:

| Задача | Интервал | Назначение |
|--------|----------|------------|
| `sync_all_products_task` | 6 часов | Синхронизация продуктов |
| `sync_all_sales_task` | 1 час | Синхронизация продаж |
| `sync_all_reviews_task` | 2 часа | Синхронизация отзывов |
| `check_stock_levels_task` | 30 минут | Проверка остатков |

**Проверка в Flower UI:**

1. Откройте http://localhost:5555
2. Перейдите в раздел "Tasks"
3. Должны отображаться периодически выполняемые задачи

**Проверка в логах:**

```bash
# Должны увидеть записи вида:
# [INFO] Received task: tasks.sync.sync_all_products_task
# [INFO] Task tasks.sync.sync_all_products_task[abc123] succeeded
```

---

## Шаг 6: Остановка сервисов

### Docker:

```bash
cd backend
docker-compose down
```

### Локальный запуск:

Нажмите `Ctrl+C` в каждом терминале.

---

## Troubleshooting

### Проблема: "Connection refused" при запуске задач

**Причина:** Redis или Celery Worker не запущены.

**Решение:**

```bash
# Проверить Redis
redis-cli ping
# Ответ: PONG

# Проверить Celery Worker
docker ps | grep celery_worker
```

---

### Проблема: Задача зависла (статус PENDING)

**Причина:** Celery Worker не обрабатывает задачи.

**Решение:**

```bash
# Перезапустить worker
docker restart ai_marketplace_celery_worker

# Или локально
# Остановить worker (Ctrl+C) и запустить снова
./backend/scripts/start_celery_worker.sh
```

---

### Проблема: "ModuleNotFoundError" в логах Celery

**Причина:** Неправильный PYTHONPATH.

**Решение:**

Убедитесь, что `PYTHONPATH` установлен:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

Или измените в скриптах `start_celery_worker.sh` и `start_celery_beat.sh`.

---

## Результат

После выполнения всех шагов:

✅ Redis работает  
✅ Celery Worker запущен  
✅ Celery Beat запущен  
✅ Flower UI доступен  
✅ Задачи можно запускать через API  
✅ Статус задач отображается корректно  
✅ Периодические задачи выполняются по расписанию  

**Этап 4 работает корректно!** 🎉

---

**Готовы к переходу на Этап 5 (Orchestrator).**
