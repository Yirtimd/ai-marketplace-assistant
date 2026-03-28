# 🔍 Архитектурная проверка — Этап 2

## Дата проверки: 9 марта 2026

---

## 1. Размер WildberriesService (~511 строк)

### Текущее состояние:
- **Один большой сервис** с 15 методами
- Методы сгруппированы по доменам (Products, Feedbacks, Questions, Sales)
- Общий HTTP клиент (`_make_request`)

### Анализ Single Responsibility:

**❌ НАРУШАЕТ принцип SRP**

WildberriesService отвечает за:
1. Products (5 методов)
2. Feedbacks (4 метода)
3. Questions (3 метода)  
4. Sales/Reports (3 метода)
5. HTTP коммуникацию

### Рекомендация: ✅ РАЗДЕЛИТЬ НА МОДУЛИ

**Предлагаемая структура:**

```
backend/services/wildberries/
├── __init__.py
├── base.py                 # Базовый HTTP клиент
├── products.py             # WBProductsService
├── feedbacks.py            # WBFeedbacksService  
├── sales.py                # WBSalesService
└── exceptions.py           # Исключения
```

**Преимущества:**
- ✅ Каждый сервис отвечает за одну domain area
- ✅ Легче тестировать
- ✅ Легче расширять
- ✅ Соответствует микросервисной архитектуре

**Как реализовать:**

```python
# base.py
class WBBaseService:
    """Base service with HTTP client"""
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
    
    async def _make_request(self, method, endpoint, ...):
        # HTTP logic
        pass

# products.py
class WBProductsService(WBBaseService):
    """Service for products operations"""
    async def get_products(self, limit, offset):
        pass
    
    async def get_product_by_id(self, nm_id):
        pass

# feedbacks.py
class WBFeedbacksService(WBBaseService):
    """Service for feedbacks and questions"""
    async def get_feedbacks(self, ...):
        pass
```

**Facade для обратной совместимости:**

```python
# __init__.py
class WildberriesService:
    """Unified facade for all WB services"""
    def __init__(self):
        self.products = WBProductsService()
        self.feedbacks = WBFeedbacksService()
        self.sales = WBSalesService()
```

**Использование:**

```python
wb = get_wb_service()
products = await wb.products.get_products(limit=10)
feedbacks = await wb.feedbacks.get_feedbacks()
```

---

## 2. Mock API режим

### Текущее состояние:

**✅ ПРАВИЛЬНО РЕАЛИЗОВАНО**

```python
self.base_url = base_url or settings.wb_api_url
# Переключение через .env:
# WB_API_URL=http://localhost:8001  # Mock
# WB_API_URL=https://api.wb.ru      # Real
```

### Анализ:

**Плюсы:**
- ✅ Mock и Real API не смешаны
- ✅ Переключение через конфигурацию
- ✅ Нет mock-специфичного кода в сервисе
- ✅ Сервис агностичен к источнику данных

**Минусы:**
- ⚠️ Нет проверки режима (dev/prod)
- ⚠️ Нет предупреждений при использовании Mock в prod

### Рекомендация: ✅ ДОБАВИТЬ РЕЖИМЫ

```python
# config/settings.py
class Settings(BaseSettings):
    environment: str = Field(default="development")  # development, staging, production
    wb_api_url: str
    wb_api_mode: str = Field(default="mock")  # mock, real

# services/wildberries/base.py
class WBBaseService:
    def __init__(self):
        if settings.environment == "production" and settings.wb_api_mode == "mock":
            logger.warning("⚠️ Using Mock API in PRODUCTION mode!")
        
        logger.info(f"WB Service mode: {settings.wb_api_mode}")
```

**Итог:** Текущая реализация корректна, но можно улучшить безопасность.

---

## 3. Структура Pydantic схем

### Текущее состояние:

**❌ ВСЕ СХЕМЫ В ОДНОМ ФАЙЛЕ**

`backend/schemas/wb_schemas.py` — 243 строки, 20+ моделей

### Проблемы:

1. **Нарушение модульности** — сложно найти нужную схему
2. **Сложно поддерживать** — файл будет расти
3. **Импорты громоздкие** — приходится импортировать из одного файла

### Рекомендация: ✅ РАЗДЕЛИТЬ ПО ДОМЕНАМ

**Предлагаемая структура:**

```
backend/schemas/
├── __init__.py
├── product.py          # Product, ProductSize, ProductPhoto, etc.
├── feedback.py         # Feedback, FeedbackAnswer, AnswerFeedbackRequest
├── question.py         # Question, QuestionAnswer, AnswerQuestionRequest  
├── sale.py             # Sale, Order, Stock
└── common.py           # Category, Subject, Brand (общие)
```

**Преимущества:**
- ✅ Логическая группировка
- ✅ Легче найти нужную схему
- ✅ Параллельная разработка
- ✅ Чистые импорты

**Пример реализации:**

```python
# product.py
from pydantic import BaseModel
from typing import List

class ProductSize(BaseModel):
    techSize: str
    wbSize: str
    price: int

class Product(BaseModel):
    nmID: int
    title: str
    sizes: List[ProductSize]

# __init__.py
from .product import Product, ProductSize
from .feedback import Feedback, FeedbackAnswer
from .sale import Sale, Stock

__all__ = ["Product", "ProductSize", "Feedback", "Sale", "Stock"]
```

**Использование:**

```python
from backend.schemas import Product, Feedback, Sale
# или
from backend.schemas.product import Product, ProductSize
```

---

## 4. Архитектура API routes

### Текущее состояние:

**✅ ПРАВИЛЬНО РЕАЛИЗОВАНО**

```python
# API endpoint
@router.get("/products/")
async def get_products(wb: WildberriesService = Depends(get_wb_service)):
    data = await wb.get_products(limit=limit)  # ← вызов сервиса
    return ProductsListResponse(**data)
```

**Схема:**
```
API endpoint
    ↓
WildberriesService  
    ↓
Wildberries API (Real или Mock)
```

### Анализ:

**✅ Соответствует архитектуре:**
- Endpoints НЕ вызывают WB API напрямую
- Используется Service Layer
- Dependency Injection работает корректно

**Минусы:**
- ⚠️ Нет кеширования
- ⚠️ Нет обработки rate limiting
- ⚠️ Нет retry логики

### Рекомендация: ✅ ДОБАВИТЬ В БУДУЩЕМ

Для Этапа 2 архитектура **КОРРЕКТНА**.

В будущем (Этап 4) добавить:
- Кеширование в Redis
- Retry механизм
- Rate limiting handling

---

## 5. Data Ingestion (поток данных)

### Текущее состояние:

**СХЕМА:**
```
WB API → Service → API endpoint → Frontend (JSON)
```

**Данные НЕ сохраняются в БД!**

### Анализ:

**✅ ДЛЯ ЭТАПА 2 — ПРАВИЛЬНО**

Этап 2 из ROADMAP.md:
> "Цель этапа: получить доступ к данным магазина"

Сохранение в БД — это **Этап 3** (Модель данных)

### Подготовка к Этапу 3:

**ГОТОВО ✅:**
- Base модель создана (`database/base.py`)
- PostgreSQL подключен
- Структура `database/models/` готова
- Pydantic схемы можно конвертировать в SQLAlchemy модели

**Будущая схема (Этап 3):**
```
WB API
    ↓
Service (получение данных)
    ↓
Data Transformation Layer  # ← НОВЫЙ
    ↓
Database Models (SQLAlchemy)
    ↓
PostgreSQL
```

**Рекомендация для Этапа 3:**

Создать слой трансформации:

```python
# backend/services/data_sync.py
class DataSyncService:
    """Синхронизация данных из WB в БД"""
    
    async def sync_products(self):
        # 1. Получить из WB
        wb_products = await wb_service.get_products()
        
        # 2. Трансформировать
        db_products = self._transform_products(wb_products)
        
        # 3. Сохранить в БД
        await self._save_to_db(db_products)
```

---

## 6. Готовность к Этапу 3

### Текущая архитектура:
```
WB API → Service → API endpoint → Frontend
```

### Целевая архитектура (Этап 3):
```
WB API → Service → Data Transformation → DB Models → PostgreSQL
                                              ↓
                                         API endpoint → Frontend
```

### Проверка готовности:

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| **Base модель** | ✅ Готово | `database/base.py` создан |
| **PostgreSQL** | ✅ Готово | Подключен и работает |
| **Pydantic схемы** | ✅ Готово | Можно конвертировать в ORM |
| **WB Service** | ✅ Готово | Получает данные |
| **Data sync layer** | ❌ Нет | Нужно создать |
| **SQLAlchemy модели** | ❌ Нет | Нужно создать |

### Рекомендации для Этапа 3:

1. **Создать SQLAlchemy модели:**
```python
# database/models/product.py
from backend.database.base import Base

class Product(Base):
    __tablename__ = "products"
    
    nm_id: Mapped[int] = mapped_column(unique=True)
    vendor_code: Mapped[str]
    brand: Mapped[str]
    title: Mapped[str]
    # ... остальные поля
```

2. **Создать Data Sync Service:**
```python
# services/data_sync.py
class DataSyncService:
    async def sync_products_from_wb(self):
        # Получить из WB → Сохранить в БД
        pass
```

3. **Настроить Alembic миграции:**
```bash
alembic revision --autogenerate -m "Add product models"
alembic upgrade head
```

**ВЫВОД:** Архитектура готова к Этапу 3 на **90%**

---

## 7. Общая архитектурная оценка

### 7.1 Соответствие ARCHITECTURE.md

**Проверка:**

| Требование | Реализация | Статус |
|------------|------------|--------|
| Service Layer | WildberriesService | ✅ Есть |
| Разделение на слои | API → Service → External | ✅ Правильно |
| Stateless сервисы | Нет внутреннего состояния | ✅ Правильно |
| Модульность | Один большой сервис | ⚠️ Можно улучшить |

**Итог:** Соответствует на **85%**

**Что улучшить:**
- Разделить WildberriesService на модули

---

### 7.2 Соответствие PROJECT_RULES.md

**Проверка правил:**

| Правило | Статус | Комментарий |
|---------|--------|-------------|
| Модульная архитектура | ⚠️ Частично | Сервис большой |
| Разделение ответственности | ✅ Да | Слои разделены |
| Не вызывать API напрямую | ✅ Да | Через service |
| Структура папок | ✅ Да | Соответствует |
| Использование services/ | ✅ Да | WB в services/ |

**Итог:** Соответствует на **90%**

**Что улучшить:**
- Разделить большой сервис

---

### 7.3 Соответствие DEVELOPMENT_WORKFLOW.md

**Проверка процесса:**

| Критерий | Статус |
|----------|--------|
| Последовательная разработка | ✅ Да |
| Сначала backend, потом UI | ✅ Да |
| Использование service layer | ✅ Да |
| Документирование | ✅ Да |

**Итог:** Соответствует на **100%** ✅

---

## ИТОГОВАЯ ОЦЕНКА

### Архитектурные проблемы:

1. **🔴 КРИТИЧНО:** Большой WildberriesService (нарушает SRP)
2. **🟡 СРЕДНЕЕ:** Все Pydantic схемы в одном файле
3. **🟢 НИЗКОЕ:** Нет режимов работы (dev/prod)

### Рекомендации (приоритеты):

#### Высокий приоритет (до Этапа 3):
1. ✅ **Разделить WildberriesService на модули**
2. ✅ **Разделить Pydantic схемы по файлам**

#### Средний приоритет (Этап 3):
3. ✅ **Добавить режимы работы (dev/prod)**
4. ✅ **Создать Data Sync Layer**

#### Низкий приоритет (Этап 4+):
5. ✅ **Добавить кеширование**
6. ✅ **Добавить retry логику**

---

## ПЛАН РЕФАКТОРИНГА

### Фаза 1: Разделение сервисов (2-3 часа)

```
backend/services/wildberries/
├── __init__.py              # Facade + exports
├── base.py                  # WBBaseService
├── products.py              # WBProductsService
├── feedbacks.py             # WBFeedbacksService
├── sales.py                 # WBSalesService
└── exceptions.py            # Исключения
```

### Фаза 2: Разделение схем (1-2 часа)

```
backend/schemas/
├── __init__.py              # Exports
├── product.py               # Product схемы
├── feedback.py              # Feedback схемы
├── question.py              # Question схемы
├── sale.py                  # Sale схемы
└── common.py                # Общие схемы
```

### Фаза 3: Обновление импортов (30 мин)

- Обновить импорты в роутерах
- Обновить dependency injection
- Протестировать

---

## ВЫВОД

### Текущая реализация:

**Оценка: 8/10** 🟢

**Плюсы:**
- ✅ Service Layer правильно реализован
- ✅ Разделение на слои корректно
- ✅ Mock API интеграция чистая
- ✅ Dependency Injection работает
- ✅ Готовность к Этапу 3 высокая

**Минусы:**
- ⚠️ WildberriesService слишком большой
- ⚠️ Pydantic схемы не разделены
- ⚠️ Нет режимов dev/prod

### Рекомендация:

**Можно продолжать разработку**, но желательно провести рефакторинг **перед Этапом 3**.

Альтернатива: Провести рефакторинг **в начале Этапа 3**, когда будем создавать модели БД.

---

**Дата проверки:** 9 марта 2026  
**Проверил:** AI Architect  
**Статус:** ✅ ОДОБРЕНО С РЕКОМЕНДАЦИЯМИ
