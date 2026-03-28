# Архитектурный аудит Этапа 3: Data Model + Data Sync

**Дата проверки:** 12 марта 2026  
**Оценка:** 7.5/10 🟡

---

## Executive Summary

### ✅ Сильные стороны

1. **Модульная структура** - отличное разделение WB сервисов и схем
2. **Repository Pattern** - правильная реализация слоя доступа к данным
3. **Базовая архитектура** - корректный data flow WB API → Service → Sync → Repository → DB
4. **Relationships** - правильные связи между моделями
5. **Task/Event модели** - готовность к Celery и event-driven архитектуре

### ⚠️ Критические проблемы

1. **🔴 CRITICAL: Отсутствие historical tracking** - нет таблиц для истории цен и остатков
2. **🔴 CRITICAL: Неправильная стратегия sync_sales** - использует update вместо append
3. **🟡 MEDIUM: Недостаточно полей в Product** для аналитики
4. **🟡 MEDIUM: Отсутствие soft delete** в критических таблицах

---

## 1. Проверка структуры модели Product

### Текущие поля

```python
# Есть:
✅ nm_id (int) - WB ID товара
✅ vendor_code (str) - артикул поставщика  
✅ brand (str) - бренд
✅ category (str) - категория
✅ subject_name (str) - предмет
✅ price (Numeric) - цена
✅ discount (Numeric) - скидка
✅ rating (Numeric) - рейтинг
✅ reviews_count (int) - количество отзывов
✅ sizes (JSON) - размеры
✅ photos (JSON) - фото
✅ characteristics (JSON) - характеристики
```

### ❌ Недостающие поля для аналитики

| Поле | Тип | Зачем нужно | Приоритет |
|------|-----|-------------|-----------|
| `current_stock` | Integer | Текущие остатки для быстрого доступа | HIGH |
| `stock_in_warehouse` | Integer | Остатки на складе WB | MEDIUM |
| `stock_in_transit` | Integer | Товар в пути к клиенту | MEDIUM |
| `position_in_search` | Integer | Позиция в поиске (для SEO аналитики) | LOW |
| `views_count` | Integer | Количество просмотров | MEDIUM |
| `conversion_rate` | Numeric(5,2) | Конверсия (продажи/просмотры) | MEDIUM |
| `avg_delivery_days` | Integer | Средний срок доставки | LOW |
| `is_active` | Boolean | Активен ли товар в продаже | HIGH |
| `last_sync_at` | DateTime | Последняя синхронизация | HIGH |

### 🔧 Рекомендуемые изменения Product

```python
class Product(Base):
    # ... existing fields ...
    
    # Inventory tracking
    current_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_in_warehouse: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_in_transit: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Analytics
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversion_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
```

**Оценка:** 6/10 - базовые поля есть, но для AI аналитики нужно больше данных

---

## 2. Проверка модели Sale

### ✅ Положительные моменты

```python
✅ sale_date (DateTime, indexed) - поддержка временных рядов
✅ quantity (Integer) - количество товаров
✅ product_id (FK) - связь с товаром
✅ price, discount, total_price - полная финансовая информация
✅ warehouse, region - геоаналитика
✅ sale_id (unique) - предотвращение дубликатов
```

### ✅ Временные ряды - поддержка есть

Модель **полностью поддерживает** анализ временных рядов:
- Индекс на `sale_date` ✅
- Связь с `Product` ✅
- Количество товаров ✅

**Можно строить:**
- Анализ трендов ✅
- Прогноз продаж ✅
- Динамику продаж ✅
- Revenue metrics ✅

### ⚠️ Недостающие поля

| Поле | Тип | Зачем нужно | Приоритет |
|------|-----|-------------|-----------|
| `return_date` | DateTime | Дата возврата (для расчета churn) | MEDIUM |
| `is_returned` | Boolean | Флаг возврата | HIGH |
| `return_reason` | String | Причина возврата | LOW |
| `commission_percent` | Numeric(5,2) | Процент комиссии WB | HIGH |
| `commission_amount` | Numeric(10,2) | Сумма комиссии | HIGH |
| `net_revenue` | Numeric(10,2) | Чистая выручка | HIGH |

### 🔧 Рекомендуемые изменения Sale

```python
class Sale(Base):
    # ... existing fields ...
    
    # Returns tracking
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    return_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    return_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Financial analytics
    commission_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    commission_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    net_revenue: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
```

**Оценка:** 8/10 - хорошая основа для временных рядов, но не хватает финансовой детализации

---

## 3. 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА: Отсутствие historical tracking

### Проблема

Для AI аналитики **критически важно** хранить историю изменений:

1. **Price History** - изменения цен
2. **Stock History** - изменения остатков
3. **Rating History** - динамика рейтинга

**Текущая реализация:**
```python
# Product модель - только текущее состояние ❌
price: Mapped[float] = ...
rating: Mapped[float] = ...
```

При обновлении товара старые данные **теряются**.

### 🚨 Последствия отсутствия истории

| Задача AI | Возможна? | Почему нет |
|-----------|-----------|------------|
| Анализ эффективности изменения цены | ❌ | Нет истории цен |
| Прогноз оптимальной цены | ❌ | Нет данных для обучения модели |
| Анализ влияния остатков на продажи | ❌ | Нет истории остатков |
| Корреляция рейтинга и продаж | ❌ | Нет истории рейтинга |
| A/B тестирование цен | ❌ | Невозможно отследить эффект |

### 🔧 Решение: Добавить таблицы истории

#### 3.1. PriceHistory

```python
class PriceHistory(Base):
    """Price change history for products"""
    __tablename__ = "price_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=True)  # "wb_sync", "manual", "ai_recommendation"
    
    product: Mapped["Product"] = relationship("Product")
```

**Применение:**
- Анализ динамики цен
- Расчет ценовой эластичности
- A/B тестирование цен
- Прогноз оптимальной цены

#### 3.2. StockHistory

```python
class StockHistory(Base):
    """Stock level history for products"""
    __tablename__ = "stock_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    stock_total: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_warehouse: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_in_transit: Mapped[int] = mapped_column(Integer, nullable=False)
    
    warehouse_id: Mapped[int] = mapped_column(Integer, nullable=True)
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    product: Mapped["Product"] = relationship("Product")
```

**Применение:**
- Прогноз окончания товара
- Расчет velocity (скорости продаж)
- Оптимизация закупок
- Анализ stockout events

#### 3.3. RatingHistory

```python
class RatingHistory(Base):
    """Rating change history for products"""
    __tablename__ = "rating_history"
    
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    product: Mapped["Product"] = relationship("Product")
```

**Применение:**
- Корреляция рейтинга и продаж
- Анализ влияния отзывов
- Мониторинг изменений репутации

### 📊 Индексы для эффективных запросов

```python
# Composite indexes for time-series queries
Index('idx_price_history_product_time', 'product_id', 'changed_at')
Index('idx_stock_history_product_time', 'product_id', 'recorded_at')
Index('idx_rating_history_product_time', 'product_id', 'recorded_at')
```

**Оценка:** 2/10 - критическая нехватка historical tracking

---

## 4. 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА: DataSyncService стратегия

### Текущая реализация

```python
# sync_sales() - строки 153-177
existing_sale = await sale_repository.get_by_field(db, "sale_id", sale_id)

if existing_sale:
    await sale_repository.update(db, existing_sale.id, sale_data)  # ❌ UPDATE
    updated += 1
else:
    await sale_repository.create(db, sale_data)  # ✅ CREATE
    created += 1
```

### 🚨 Проблема

**Sales данные - это исторические записи!**

Каждая продажа должна быть **immutable** (неизменяемой).

**Текущее поведение:**
```
Day 1: Sale #123 → создана запись
Day 2: Sale #123 → ПЕРЕЗАПИСАНА (updated += 1) ❌
```

**Правильное поведение:**
```
Day 1: Sale #123 → создана запись
Day 2: Sale #123 → пропущена (already exists)
```

### 📊 Правильная стратегия sync

| Тип данных | Стратегия | Пример |
|------------|-----------|--------|
| **Sales** | APPEND only (skip if exists) | Продажи - исторические данные |
| **Reviews** | APPEND only | Отзывы - исторические данные |
| **Products** | UPDATE | Товары - текущее состояние |
| **Stocks** | UPDATE + History | Остатки - текущее + история |
| **Prices** | UPDATE + History | Цены - текущее + история |

### 🔧 Исправление sync_sales()

```python
async def sync_sales(
    self,
    db: AsyncSession,
    shop_id: int,
    date_from: datetime = None,
    date_to: datetime = None
) -> Dict[str, Any]:
    """
    Sync sales from WB to database
    
    Strategy: APPEND ONLY (sales are immutable historical records)
    """
    created = 0
    skipped = 0  # Вместо updated
    errors = 0
    
    try:
        wb_response = await self.sales_service.get_sales(date_from=date_from, date_to=date_to)
        wb_sales = wb_response.get("data", [])
        
        for wb_sale in wb_sales:
            try:
                sale_id = wb_sale.get("saleID")
                
                # Check if sale already exists
                existing_sale = await sale_repository.get_by_field(db, "sale_id", sale_id)
                
                if existing_sale:
                    # Sales are immutable - skip if exists ✅
                    logger.debug(f"Sale {sale_id} already exists, skipping")
                    skipped += 1
                    continue
                
                # Create new sale
                nm_id = wb_sale.get("nmID")
                product = await product_repository.get_by_nm_id(db, nm_id)
                
                if not product:
                    logger.warning(f"Product {nm_id} not found for sale {sale_id}")
                    continue
                
                sale_data = {
                    "shop_id": shop_id,
                    "product_id": product.id,
                    "sale_id": sale_id,
                    # ... other fields ...
                }
                
                await sale_repository.create(db, sale_data)
                created += 1
            
            except Exception as e:
                logger.error(f"Error syncing sale {wb_sale.get('saleID')}: {e}")
                errors += 1
        
        logger.info(f"Sales sync completed: created={created}, skipped={skipped}, errors={errors}")
        
        return {
            "status": "completed",
            "created": created,
            "skipped": skipped,  # Changed from "updated"
            "errors": errors,
            "total": len(wb_sales)
        }
    
    except Exception as e:
        logger.error(f"Sales sync failed: {e}")
        return {"status": "failed", "error": str(e)}
```

### 🔧 Исправление sync_reviews()

Аналогично - reviews тоже должны быть append-only:

```python
if existing_review:
    # Reviews are historical - skip if exists ✅
    skipped += 1
    continue
else:
    await review_repository.create(db, review_data)
    created += 1
```

### 🔧 Добавить sync с историей для Products

```python
async def sync_products_with_history(
    self,
    db: AsyncSession,
    shop_id: int,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Sync products with price/stock history tracking
    """
    for wb_product in wb_products:
        existing_product = await product_repository.get_by_nm_id(db, nm_id)
        
        if existing_product:
            # Check if price changed
            new_price = wb_product.get("price")
            if existing_product.price != new_price:
                # Save to PriceHistory
                await price_history_repository.create(db, {
                    "product_id": existing_product.id,
                    "price": new_price,
                    "changed_at": datetime.utcnow(),
                    "source": "wb_sync"
                })
            
            # Check if stock changed
            new_stock = wb_product.get("stock")
            if existing_product.current_stock != new_stock:
                # Save to StockHistory
                await stock_history_repository.create(db, {
                    "product_id": existing_product.id,
                    "stock_total": new_stock,
                    "recorded_at": datetime.utcnow()
                })
            
            # Update product with new values
            await product_repository.update(db, existing_product.id, product_data)
```

**Оценка:** 4/10 - критическая ошибка в стратегии синхронизации

---

## 5. Проверка ingestion архитектуры

### Целевой pipeline

```
Scheduler (Celery Beat)
    ↓
Task (создание записи в БД)
    ↓
Celery Worker (выполнение)
    ↓
DataSyncService
    ↓
WB Service
    ↓
Repository
    ↓
Database
```

### ✅ Текущая готовность

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| **Task модель** | ✅ READY | Поля: celery_task_id, status, scheduled_at |
| **DataSyncService** | ✅ READY | Async методы, независим от контекста |
| **WB Services** | ✅ READY | Модульные, stateless |
| **Repositories** | ✅ READY | Async, с error handling |
| **Database** | ✅ READY | AsyncSession поддержка |

### ✅ DataSyncService - вызов из tasks

```python
# Пример будущего Celery task
@celery_app.task
async def sync_products_task(shop_id: int):
    async with async_session() as db:
        # Get services
        products_service = WBProductsService()
        feedbacks_service = WBFeedbacksService()
        sales_service = WBSalesService()
        
        # Create DataSyncService
        sync_service = DataSyncService(
            products_service,
            feedbacks_service,
            sales_service
        )
        
        # Run sync ✅
        result = await sync_service.sync_products(db, shop_id)
        
        return result
```

### ⚠️ Недостающие компоненты

1. **Task Repository** - для управления Task записями
2. **Event logging в DataSyncService** - запись в Event модель
3. **Task status tracking** - обновление статуса задачи
4. **Retry logic** - для failed syncs

### 🔧 Рекомендации

```python
# Добавить в DataSyncService
class DataSyncService:
    def __init__(self, ..., task_id: Optional[int] = None):
        self.task_id = task_id
    
    async def _log_event(self, db: AsyncSession, level: str, message: str):
        """Log sync events"""
        if self.task_id:
            await event_repository.create(db, {
                "task_id": self.task_id,
                "event_type": "data_sync",
                "event_level": level,
                "message": message,
                "source": "DataSyncService"
            })
    
    async def sync_products(self, ...):
        await self._log_event(db, "info", "Starting products sync")
        # ... sync logic ...
        await self._log_event(db, "info", f"Completed: {created} created")
```

**Оценка:** 8/10 - архитектура готова, нужны небольшие доработки

---

## 6. Проверка Task/Event/WorkflowState архитектуры

### ✅ Task модель - отлично

```python
class Task(Base):
    ✅ user_id, shop_id - связь с контекстом
    ✅ task_type - типизация задач
    ✅ status (enum) - отслеживание состояния
    ✅ priority (enum) - приоритизация
    ✅ celery_task_id - интеграция с Celery
    ✅ scheduled_at, started_at, completed_at - временная линия
    ✅ result, error - результаты выполнения
```

**Поддерживает:**
- Celery интеграцию ✅
- Scheduling ✅
- Status tracking ✅
- Error handling ✅

### ✅ Event модель - хорошо

```python
class Event(Base):
    ✅ event_type (enum) - 6 типов событий
    ✅ event_level (enum) - severity levels
    ✅ task_id - связь с задачами
    ✅ details (JSON) - гибкость данных
    ✅ event_time (indexed) - time-series queries
```

**Поддерживает:**
- Event sourcing ✅
- Audit trail ✅
- Monitoring ✅
- AI workflows logging ✅

### ✅ WorkflowState модель - отлично

```python
class WorkflowState(Base):
    ✅ workflow_id (unique) - идентификация
    ✅ workflow_type - типизация
    ✅ status (enum) - отслеживание
    ✅ current_node - для LangGraph
    ✅ state_data (JSON) - полное состояние
    ✅ input/output_data - контракты
```

**Поддерживает:**
- LangGraph checkpoints ✅
- State persistence ✅
- Resumable workflows ✅
- Multi-agent coordination ✅

### ⚠️ Недостающее для AI workflows

1. **Workflow relationships** - связь между workflows (parent/child)
2. **Agent tracking** - какой агент выполняет узел
3. **Token usage tracking** - для AI вызовов
4. **Cost tracking** - для мониторинга расходов

### 🔧 Рекомендуемое дополнение

```python
class WorkflowState(Base):
    # ... existing fields ...
    
    # Workflow hierarchy
    parent_workflow_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    
    # Agent tracking
    current_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Cost tracking
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Numeric(10, 4), default=0, nullable=False)
```

**Оценка:** 9/10 - отличная основа для AI workflows

---

## 7. Общая архитектурная оценка

### Соответствие ARCHITECTURE.md

| Принцип | Соответствие | Комментарий |
|---------|--------------|-------------|
| **Модульная архитектура** | ✅ 9/10 | Отличное разделение services и schemas |
| **Stateless agents** | ✅ 10/10 | Все сервисы stateless |
| **Server-side state** | ✅ 9/10 | WorkflowState для хранения состояния |
| **Event-driven** | ✅ 8/10 | Event модель готова, нужна интеграция |
| **Workflow orchestration** | ✅ 9/10 | WorkflowState поддерживает LangGraph |

**Итого по ARCHITECTURE.md:** ✅ 9/10

### Соответствие PROJECT_RULES.md

| Правило | Соответствие | Комментарий |
|---------|--------------|-------------|
| **Repository Pattern** | ✅ 10/10 | Правильная реализация |
| **Service Layer** | ✅ 9/10 | Четкое разделение ответственности |
| **Type hints** | ✅ 10/10 | Везде используется Mapped |
| **Error handling** | ✅ 8/10 | Есть, но нужно больше logging |
| **Async/await** | ✅ 10/10 | Правильное использование |

**Итого по PROJECT_RULES.md:** ✅ 9/10

### Соответствие DEVELOPMENT_WORKFLOW.md

| Требование | Соответствие | Комментарий |
|------------|--------------|-------------|
| **Data Model первым** | ✅ 10/10 | Модели созданы перед логикой |
| **Migration управление** | ✅ 8/10 | Alembic настроен |
| **Тестируемость** | ✅ 7/10 | Архитектура testable, тестов нет |

**Итого по DEVELOPMENT_WORKFLOW.md:** ✅ 8/10

---

## 8. Архитектурные риски перед Этапом 4

### 🔴 КРИТИЧЕСКИЕ риски (блокируют AI аналитику)

1. **Отсутствие PriceHistory/StockHistory/RatingHistory**
   - **Риск:** AI не сможет анализировать динамику и тренды
   - **Действие:** Добавить 3 таблицы истории ПЕРЕД Этапом 4
   - **Приоритет:** URGENT

2. **Неправильная sync стратегия для Sales/Reviews**
   - **Риск:** Потеря исторических данных при повторной синхронизации
   - **Действие:** Изменить на append-only стратегию
   - **Приоритет:** URGENT

### 🟡 ВЫСОКИЕ риски (снизят качество аналитики)

3. **Недостаточно полей в Product для аналитики**
   - **Риск:** AI не сможет строить качественные прогнозы
   - **Действие:** Добавить поля: current_stock, is_active, last_sync_at
   - **Приоритет:** HIGH

4. **Отсутствие финансовых полей в Sale**
   - **Риск:** Невозможен расчет чистой прибыли
   - **Действие:** Добавить: commission_amount, net_revenue, is_returned
   - **Приоритет:** HIGH

### 🟢 СРЕДНИЕ риски (не критично)

5. **Отсутствие soft delete**
   - **Риск:** Потеря данных при случайном удалении
   - **Действие:** Добавить deleted_at во все модели
   - **Приоритет:** MEDIUM

6. **Нет Event logging в DataSyncService**
   - **Риск:** Сложно отследить проблемы синхронизации
   - **Действие:** Добавить event_repository.create() в sync методах
   - **Приоритет:** MEDIUM

---

## 9. План действий перед Этапом 4

### MUST DO (блокеры)

1. ✅ **Создать таблицы истории**
   - [ ] `database/models/price_history.py`
   - [ ] `database/models/stock_history.py`
   - [ ] `database/models/rating_history.py`
   - [ ] Создать repositories для них
   - [ ] Создать миграцию

2. ✅ **Исправить DataSyncService**
   - [ ] `sync_sales()` → append-only стратегия
   - [ ] `sync_reviews()` → append-only стратегия
   - [ ] `sync_products()` → добавить history tracking
   - [ ] Добавить Event logging

3. ✅ **Дополнить Product модель**
   - [ ] Добавить: current_stock, is_active, last_sync_at
   - [ ] Создать миграцию

4. ✅ **Дополнить Sale модель**
   - [ ] Добавить: is_returned, commission_amount, net_revenue
   - [ ] Создать миграцию

### SHOULD DO (улучшения)

5. **Добавить Task Repository**
6. **Добавить soft delete**
7. **Добавить cost tracking в WorkflowState**

---

## 10. Итоговая оценка

| Категория | Оценка | Комментарий |
|-----------|--------|-------------|
| **Модульность** | 9/10 | Отличная структура |
| **Data Model** | 6/10 | Нужны history таблицы |
| **Data Sync** | 5/10 | Критическая ошибка в стратегии |
| **Ingestion готовность** | 8/10 | Почти готова к Celery |
| **AI workflows готовность** | 9/10 | Task/Event/WorkflowState отлично |
| **Архитектурное соответствие** | 9/10 | Следует всем документам |

### **ОБЩАЯ ОЦЕНКА: 7.5/10** 🟡

**Вердикт:** Архитектура **хорошая**, но есть **2 критических проблемы**:
1. Отсутствие historical tracking (блокирует AI аналитику)
2. Неправильная sync стратегия (потеря данных)

**Рекомендация:** Исправить критические проблемы **ДО** начала Этапа 4.

---

## Файлы для создания

### Новые модели

```
backend/database/models/
├── price_history.py      # NEW
├── stock_history.py      # NEW
└── rating_history.py     # NEW
```

### Новые repositories

```
backend/database/repositories/
├── price_history.py      # NEW
├── stock_history.py      # NEW
├── rating_history.py     # NEW
└── task.py               # NEW
```

### Миграции

```
alembic/versions/
└── YYYYMMDD_HHMM-xxxxx_add_history_tables.py    # NEW
└── YYYYMMDD_HHMM-xxxxx_enhance_product_sale.py  # NEW
```

---

**Конец отчета**
