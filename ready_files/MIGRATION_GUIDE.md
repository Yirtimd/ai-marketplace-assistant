# Подробное руководство: Миграции базы данных

**Дата:** 12 марта 2026  
**Цель:** Применить изменения Этапа 3 к базе данных

---

## Содержание

1. [Что изменилось](#что-изменилось)
2. [Шаг 1: Обновление standalone моделей](#шаг-1-обновление-standalone-моделей)
3. [Шаг 2: Создание миграции](#шаг-2-создание-миграции)
4. [Шаг 3: Применение миграции](#шаг-3-применение-миграции)
5. [Проверка](#проверка)
6. [Откат (если нужно)](#откат-если-нужно)
7. [Troubleshooting](#troubleshooting)

---

## Что изменилось

### 📊 Статистика изменений

| Тип изменения | Количество |
|---------------|------------|
| **Новые таблицы** | 3 (price_history, stock_history, rating_history) |
| **Изменено таблиц** | 2 (products, sales) |
| **Новых полей в products** | 10 |
| **Новых полей в sales** | 6 |
| **Новых индексов** | 6 |

### 📋 Детальный список изменений

#### 1. Новая таблица: `price_history`

```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(5,2),
    final_price NUMERIC(10,2) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    source VARCHAR(50)
);

CREATE INDEX idx_price_history_product_time ON price_history(product_id, changed_at);
CREATE INDEX idx_price_history_product ON price_history(product_id);
CREATE INDEX idx_price_history_changed_at ON price_history(changed_at);
```

**Назначение:** Хранение истории изменений цен для:
- Анализа ценовой эластичности
- A/B тестирования цен
- Прогноза оптимальной цены

#### 2. Новая таблица: `stock_history`

```sql
CREATE TABLE stock_history (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    stock_total INTEGER NOT NULL,
    stock_warehouse INTEGER NOT NULL,
    stock_in_transit INTEGER NOT NULL,
    warehouse_id INTEGER,
    warehouse_name VARCHAR(255),
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    source VARCHAR(50)
);

CREATE INDEX idx_stock_history_product_time ON stock_history(product_id, recorded_at);
CREATE INDEX idx_stock_history_product ON stock_history(product_id);
CREATE INDEX idx_stock_history_recorded_at ON stock_history(recorded_at);
```

**Назначение:** Хранение истории остатков для:
- Прогноза stockout
- Расчета velocity продаж
- Оптимизации закупок

#### 3. Новая таблица: `rating_history`

```sql
CREATE TABLE rating_history (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    rating NUMERIC(3,2) NOT NULL,
    reviews_count INTEGER NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rating_history_product_time ON rating_history(product_id, recorded_at);
CREATE INDEX idx_rating_history_product ON rating_history(product_id);
CREATE INDEX idx_rating_history_recorded_at ON rating_history(recorded_at);
```

**Назначение:** Хранение истории рейтинга для:
- Корреляции рейтинга и продаж
- Мониторинга репутации
- Анализа влияния отзывов

#### 4. Изменения в таблице `products`

**Добавляемые поля:**

```sql
ALTER TABLE products 
    ADD COLUMN current_stock INTEGER DEFAULT 0 NOT NULL,
    ADD COLUMN stock_in_warehouse INTEGER DEFAULT 0 NOT NULL,
    ADD COLUMN stock_in_transit INTEGER DEFAULT 0 NOT NULL,
    ADD COLUMN views_count INTEGER DEFAULT 0 NOT NULL,
    ADD COLUMN conversion_rate NUMERIC(5,2),
    ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL,
    ADD COLUMN last_sync_at TIMESTAMP;

CREATE INDEX idx_products_is_active ON products(is_active);
```

**Итого в products:** 26 полей → 36 полей

#### 5. Изменения в таблице `sales`

**Добавляемые поля:**

```sql
ALTER TABLE sales
    ADD COLUMN commission_percent NUMERIC(5,2),
    ADD COLUMN commission_amount NUMERIC(10,2),
    ADD COLUMN net_revenue NUMERIC(10,2),
    ADD COLUMN is_returned BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN return_date TIMESTAMP,
    ADD COLUMN return_reason VARCHAR(255);

CREATE INDEX idx_sales_is_returned ON sales(is_returned);
```

**Итого в sales:** 18 полей → 24 поля

---

## Шаг 1: Обновление standalone моделей

### ✅ Уже выполнено!

Файл `backend/alembic/models_standalone.py` уже обновлен со всеми изменениями:

- ✅ Product модель расширена
- ✅ Sale модель расширена
- ✅ Добавлены PriceHistory, StockHistory, RatingHistory

**Проверка:**
```bash
cd backend
cat alembic/models_standalone.py | grep "class PriceHistory"
cat alembic/models_standalone.py | grep "current_stock"
cat alembic/models_standalone.py | grep "commission_percent"
```

Если видите эти строки - файл обновлен правильно! ✅

---

## Шаг 2: Создание миграции

### 2.1 Убедитесь что PostgreSQL запущен

```bash
# Проверка через Docker Compose
cd backend
docker-compose ps

# Если не запущен:
docker-compose up -d postgres redis
```

**Ожидаемый вывод:**
```
NAME                COMMAND                  SERVICE    STATUS
backend-postgres-1  "docker-entrypoint.s…"   postgres   Up 5 minutes
backend-redis-1     "docker-entrypoint.s…"   redis      Up 5 minutes
```

### 2.2 Активируйте виртуальное окружение

```bash
cd backend
source venv/bin/activate
```

### 2.3 Создайте миграцию

```bash
alembic revision -m "Add history tables and enhance product and sale models"
```

**Ожидаемый вывод:**
```
Generating /path/to/backend/alembic/versions/YYYYMMDD_HHMM-xxxxx_add_history_tables_and_enhance_product_and_sale_models.py ...  done
```

**Файл миграции будет создан в:**
```
backend/alembic/versions/YYYYMMDD_HHMM-xxxxx_add_history_tables_and_enhance_product_and_sale_models.py
```

### 2.4 Отредактируйте файл миграции

Откройте созданный файл и заполните методы `upgrade()` и `downgrade()`.

**Пример содержимого:**

```python
"""Add history tables and enhance product and sale models

Revision ID: xxxxx
Revises: xxxxx
Create Date: 2026-03-12 ...

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'xxxxx'
down_revision = 'xxxxx'  # ID предыдущей миграции
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === 1. Создаем новые таблицы ===
    
    # PriceHistory
    op.create_table('price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discount', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('final_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_price_history_product', 'price_history', ['product_id'])
    op.create_index('idx_price_history_changed_at', 'price_history', ['changed_at'])
    op.create_index('idx_price_history_product_time', 'price_history', ['product_id', 'changed_at'])
    
    # StockHistory
    op.create_table('stock_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('stock_total', sa.Integer(), nullable=False),
        sa.Column('stock_warehouse', sa.Integer(), nullable=False),
        sa.Column('stock_in_transit', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=True),
        sa.Column('warehouse_name', sa.String(length=255), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stock_history_product', 'stock_history', ['product_id'])
    op.create_index('idx_stock_history_recorded_at', 'stock_history', ['recorded_at'])
    op.create_index('idx_stock_history_product_time', 'stock_history', ['product_id', 'recorded_at'])
    
    # RatingHistory
    op.create_table('rating_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('reviews_count', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rating_history_product', 'rating_history', ['product_id'])
    op.create_index('idx_rating_history_recorded_at', 'rating_history', ['recorded_at'])
    op.create_index('idx_rating_history_product_time', 'rating_history', ['product_id', 'recorded_at'])
    
    # === 2. Добавляем поля в products ===
    op.add_column('products', sa.Column('current_stock', sa.Integer(), server_default='0', nullable=False))
    op.add_column('products', sa.Column('stock_in_warehouse', sa.Integer(), server_default='0', nullable=False))
    op.add_column('products', sa.Column('stock_in_transit', sa.Integer(), server_default='0', nullable=False))
    op.add_column('products', sa.Column('views_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('products', sa.Column('conversion_rate', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('products', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('products', sa.Column('last_sync_at', sa.DateTime(), nullable=True))
    op.create_index('idx_products_is_active', 'products', ['is_active'])
    
    # === 3. Добавляем поля в sales ===
    op.add_column('sales', sa.Column('commission_percent', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('sales', sa.Column('commission_amount', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('sales', sa.Column('net_revenue', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('sales', sa.Column('is_returned', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('sales', sa.Column('return_date', sa.DateTime(), nullable=True))
    op.add_column('sales', sa.Column('return_reason', sa.String(length=255), nullable=True))
    op.create_index('idx_sales_is_returned', 'sales', ['is_returned'])


def downgrade() -> None:
    # === Откат в обратном порядке ===
    
    # 1. Удаляем индексы и поля из sales
    op.drop_index('idx_sales_is_returned', table_name='sales')
    op.drop_column('sales', 'return_reason')
    op.drop_column('sales', 'return_date')
    op.drop_column('sales', 'is_returned')
    op.drop_column('sales', 'net_revenue')
    op.drop_column('sales', 'commission_amount')
    op.drop_column('sales', 'commission_percent')
    
    # 2. Удаляем индексы и поля из products
    op.drop_index('idx_products_is_active', table_name='products')
    op.drop_column('products', 'last_sync_at')
    op.drop_column('products', 'is_active')
    op.drop_column('products', 'conversion_rate')
    op.drop_column('products', 'views_count')
    op.drop_column('products', 'stock_in_transit')
    op.drop_column('products', 'stock_in_warehouse')
    op.drop_column('products', 'current_stock')
    
    # 3. Удаляем history таблицы
    op.drop_index('idx_rating_history_product_time', table_name='rating_history')
    op.drop_index('idx_rating_history_recorded_at', table_name='rating_history')
    op.drop_index('idx_rating_history_product', table_name='rating_history')
    op.drop_table('rating_history')
    
    op.drop_index('idx_stock_history_product_time', table_name='stock_history')
    op.drop_index('idx_stock_history_recorded_at', table_name='stock_history')
    op.drop_index('idx_stock_history_product', table_name='stock_history')
    op.drop_table('stock_history')
    
    op.drop_index('idx_price_history_product_time', table_name='price_history')
    op.drop_index('idx_price_history_changed_at', table_name='price_history')
    op.drop_index('idx_price_history_product', table_name='price_history')
    op.drop_table('price_history')
```

---

## Шаг 3: Применение миграции

### 3.1 Проверьте текущий статус

```bash
alembic current
```

**Пример вывода:**
```
20260312_1317 (head)  # ваша предыдущая миграция
```

### 3.2 Посмотрите список миграций

```bash
alembic history
```

**Пример вывода:**
```
<base> -> 20260312_1317 (head), Initial database schema
20260312_1317 -> 20260312_1520, Add history tables and enhance product and sale models
```

### 3.3 Примените миграцию

```bash
alembic upgrade head
```

**Ожидаемый вывод:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 20260312_1317 -> 20260312_1520, Add history tables and enhance product and sale models
```

**✅ Миграция применена!**

---

## Проверка

### 1. Проверьте структуру таблиц

```bash
# Через psql
docker exec -it backend-postgres-1 psql -U user -d ai_marketplace -c "\dt"
```

**Должны появиться:**
```
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+--------
 public | price_history   | table | user
 public | stock_history   | table | user
 public | rating_history  | table | user
 public | products        | table | user
 public | sales           | table | user
 ... (остальные таблицы)
```

### 2. Проверьте поля в products

```bash
docker exec -it backend-postgres-1 psql -U user -d ai_marketplace -c "\d products"
```

**Должны быть новые поля:**
```
 current_stock      | integer         | not null default 0
 stock_in_warehouse | integer         | not null default 0
 stock_in_transit   | integer         | not null default 0
 views_count        | integer         | not null default 0
 conversion_rate    | numeric(5,2)    |
 is_active          | boolean         | not null default true
 last_sync_at       | timestamp       |
```

### 3. Проверьте поля в sales

```bash
docker exec -it backend-postgres-1 psql -U user -d ai_marketplace -c "\d sales"
```

**Должны быть новые поля:**
```
 commission_percent | numeric(5,2)    |
 commission_amount  | numeric(10,2)   |
 net_revenue        | numeric(10,2)   |
 is_returned        | boolean         | not null default false
 return_date        | timestamp       |
 return_reason      | character varying(255) |
```

### 4. Проверьте индексы

```bash
docker exec -it backend-postgres-1 psql -U user -d ai_marketplace -c "\di"
```

**Должны появиться:**
```
 idx_price_history_product_time
 idx_stock_history_product_time
 idx_rating_history_product_time
 idx_products_is_active
 idx_sales_is_returned
```

---

## Откат (если нужно)

### Откатить последнюю миграцию

```bash
alembic downgrade -1
```

### Откатить до конкретной версии

```bash
alembic downgrade 20260312_1317
```

### Откатить все миграции

```bash
alembic downgrade base
```

---

## Troubleshooting

### Проблема 1: "Target database is not up to date"

**Симптомы:**
```
FAILED: Target database is not up to date.
```

**Решение:**
```bash
alembic stamp head
alembic upgrade head
```

---

### Проблема 2: "Can't locate revision identified by 'xxxxx'"

**Симптомы:**
```
FAILED: Can't locate revision identified by 'xxxxx'
```

**Решение:**
Проверьте `down_revision` в файле миграции. Он должен указывать на ID предыдущей миграции.

```bash
# Посмотрите ID последней миграции
alembic current

# Откройте файл миграции и установите down_revision
```

---

### Проблема 3: "connection refused" при подключении к БД

**Симптомы:**
```
sqlalchemy.exc.OperationalError: connection refused
```

**Решение:**
```bash
# Запустите PostgreSQL
docker-compose up -d postgres

# Проверьте что запущен
docker-compose ps

# Проверьте credentials в .env
cat .env | grep DATABASE
```

---

### Проблема 4: "Column already exists"

**Симптомы:**
```
ProgrammingError: column "current_stock" of relation "products" already exists
```

**Решение:**
Миграция уже была частично применена. Нужно либо:

1. **Откатить и применить заново:**
```bash
alembic downgrade -1
alembic upgrade head
```

2. **Или вручную удалить созданные объекты:**
```bash
docker exec -it backend-postgres-1 psql -U user -d ai_marketplace

-- В psql:
ALTER TABLE products DROP COLUMN IF EXISTS current_stock;
-- ... и т.д. для всех новых полей
```

---

## Дополнительные команды

### Посмотреть SQL без применения

```bash
alembic upgrade head --sql > migration.sql
cat migration.sql
```

### Проверить что миграция применена

```bash
alembic current
```

Должно показать ID последней миграции.

### История всех миграций

```bash
alembic history --verbose
```

---

## Резюме

### ✅ Checklist выполнения

- [x] **Шаг 1:** Обновлен `alembic/models_standalone.py`
- [ ] **Шаг 2:** PostgreSQL запущен
- [ ] **Шаг 3:** Создана миграция `alembic revision -m "..."`
- [ ] **Шаг 4:** Заполнены методы upgrade() и downgrade()
- [ ] **Шаг 5:** Миграция применена `alembic upgrade head`
- [ ] **Шаг 6:** Проверены новые таблицы и поля

### 📊 Результат

После выполнения всех шагов:
- ✅ 3 новые таблицы истории в БД
- ✅ 10 новых полей в products
- ✅ 6 новых полей в sales
- ✅ 6 новых индексов
- ✅ Система готова к AI аналитике

---

**Готово к Этапу 4! 🚀**
