# Quick Start: Применение миграций

**Быстрый старт для применения изменений БД Этапа 3**

---

## TL;DR - Команды для копипаста

```bash
# 1. Запустить PostgreSQL
cd backend
docker-compose up -d postgres redis

# 2. Активировать venv
source venv/bin/activate

# 3. Создать миграцию
alembic revision -m "Add history tables and enhance models"

# 4. Применить миграцию
alembic upgrade head

# 5. Проверить
alembic current
docker exec -it backend-postgres-1 psql -U user -d ai_marketplace -c "\dt"
```

---

## Что будет создано

### 3 новые таблицы:
- `price_history` - история цен
- `stock_history` - история остатков
- `rating_history` - история рейтинга

### Новые поля в `products`:
- `current_stock`, `stock_in_warehouse`, `stock_in_transit`
- `views_count`, `conversion_rate`
- `is_active`, `last_sync_at`

### Новые поля в `sales`:
- `commission_percent`, `commission_amount`, `net_revenue`
- `is_returned`, `return_date`, `return_reason`

---

## Важно

⚠️ **Файл миграции нужно заполнить вручную!**

После команды `alembic revision` откроется файл:
```
backend/alembic/versions/YYYYMMDD_HHMM-xxxxx_add_history_tables_and_enhance_models.py
```

Скопируйте код upgrade() и downgrade() из файла:
```
ready_files/MIGRATION_GUIDE.md
```

Раздел "2.4 Отредактируйте файл миграции".

---

## Откат

```bash
# Откатить последнюю миграцию
alembic downgrade -1

# Откатить все
alembic downgrade base
```

---

## Troubleshooting

### БД не запущена
```bash
docker-compose up -d postgres
docker-compose ps
```

### Ошибка "column already exists"
```bash
alembic downgrade -1
alembic upgrade head
```

### Проверить credentials
```bash
cat .env | grep DATABASE
```

---

## Полное руководство

См. детальное руководство:
```
ready_files/MIGRATION_GUIDE.md
```

---

**После применения миграций система готова к Этапу 4!** 🚀
