# ✅ Wildberries Mock API — Готово к использованию!

## Обзор

Создан полноценный Mock API сервер для разработки AI Marketplace Assistant без доступа к реальному Wildberries API.

Дата создания: 9 марта 2026

---

## Что реализовано

### ✅ Полная имитация Wildberries API

Mock API включает все основные endpoints из официальной документации WB:

#### 1. **Работа с товарами (Products)**
- ✅ Список товаров (`/content/v2/get/cards/list`)
- ✅ Получение товара по ID
- ✅ Категории и предметы
- ✅ Характеристики товаров
- ✅ Бренды
- ✅ Создание/обновление/удаление товаров

#### 2. **Отзывы и вопросы (Feedbacks & Questions)**
- ✅ Список отзывов (`/api/v1/feedbacks`)
- ✅ Фильтрация по статусу (отвеченные/неотвеченные)
- ✅ Ответы на отзывы
- ✅ Список вопросов (`/api/v1/questions`)
- ✅ Ответы на вопросы
- ✅ Счетчики непросмотренных

#### 3. **Продажи и отчеты (Sales & Reports)**
- ✅ Отчет о продажах (`/api/v1/supplier/sales`)
- ✅ Отчет о заказах (`/api/v1/supplier/orders`)
- ✅ Отчет об остатках (`/api/v1/supplier/stocks`)
- ✅ Фильтрация по датам
- ✅ Детальные отчеты

---

## Структура Mock API

```
backend/mock_api/
├── main.py                      # FastAPI приложение
├── README.md                    # Документация
├── EXAMPLES.md                  # Примеры использования
├── start.sh                     # Startup script
│
├── models/                      # Pydantic модели
│   ├── __init__.py
│   ├── product.py              # Product, Size, Photo, etc.
│   ├── feedback.py             # Feedback, Question
│   └── sale.py                 # Sale, Order, Stock
│
├── data/                        # Тестовые данные
│   ├── __init__.py
│   ├── products.py             # 50 товаров
│   ├── feedbacks.py            # 100 отзывов + 50 вопросов
│   └── sales.py                # 200 продаж + 150 заказов + остатки
│
└── routers/                     # API endpoints
    ├── __init__.py
    ├── products.py             # Endpoints для товаров
    ├── feedbacks.py            # Endpoints для отзывов
    └── sales.py                # Endpoints для продаж
```

---

## Ключевые возможности

### 🔐 Авторизация
- Имитация авторизации по токену
- Тестовый токен: `test-api-key-12345`
- Проверка заголовка `Authorization: Bearer token`

### ⏱️ Rate Limiting
- Лимит: 3 запроса в секунду
- Burst: 6 запросов
- Имитирует реальные ограничения WB

### 📊 Реалистичные данные
- **50 товаров**: кроссовки, футболки, электроника
- **100 отзывов**: позитивные, негативные, нейтральные
- **50 вопросов** от покупателей
- **200 продаж** за последние 90 дней
- **150 заказов** (включая отмененные)
- **350+ записей остатков**

### 📚 Автоматическая документация
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI схема

### ✅ Соответствие архитектуре
- Следует `ARCHITECTURE.md`
- Модульная структура
- Pydantic модели для валидации
- Разделение на routers, models, data

---

## Запуск Mock API

### Вариант 1: Startup script

```bash
cd backend/mock_api
./start.sh
```

### Вариант 2: Напрямую

```bash
cd backend/mock_api
uvicorn main:app --reload --port 8001
```

Mock API будет доступен:
- API: `http://localhost:8001`
- Docs: `http://localhost:8001/docs`

---

## Примеры использования

### Базовый запрос

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  http://localhost:8001/content/v2/get/cards/list?limit=5
```

### Python (requests)

```python
import requests

headers = {"Authorization": "Bearer test-api-key-12345"}

# Получить товары
response = requests.get(
    "http://localhost:8001/content/v2/get/cards/list",
    headers=headers,
    params={"limit": 10}
)
products = response.json()

# Получить отзывы
response = requests.get(
    "http://localhost:8001/api/v1/feedbacks",
    headers=headers,
    params={"is_answered": False}
)
feedbacks = response.json()
```

### Python (async with httpx)

```python
import httpx

async def fetch_data():
    headers = {"Authorization": "Bearer test-api-key-12345"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8001/content/v2/get/cards/list",
            headers=headers
        )
        return response.json()
```

Подробные примеры: `backend/mock_api/EXAMPLES.md`

---

## Доступные Endpoints

### Products (Товары)
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/content/v2/get/cards/list` | Список товаров |
| GET | `/content/v2/cards/{nm_id}` | Товар по ID |
| GET | `/content/v2/object/parent/all` | Категории |
| GET | `/content/v2/object/all` | Предметы |
| GET | `/content/v2/object/charcs/{id}` | Характеристики |
| GET | `/content/v2/directory/brands` | Бренды |
| POST | `/content/v2/cards/upload` | Создать товар |
| POST | `/content/v2/cards/update` | Обновить товар |
| DELETE | `/content/v2/cards/{nm_id}` | Удалить товар |

### Feedbacks (Отзывы)
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/v1/feedbacks` | Список отзывов |
| GET | `/api/v1/feedback` | Отзыв по ID |
| GET | `/api/v1/feedbacks/count` | Количество отзывов |
| GET | `/api/v1/feedbacks/count-unanswered` | Неотвеченные |
| POST | `/api/v1/feedbacks/answer` | Ответить |
| PATCH | `/api/v1/feedbacks/answer` | Редактировать ответ |

### Questions (Вопросы)
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/v1/questions` | Список вопросов |
| GET | `/api/v1/question` | Вопрос по ID |
| GET | `/api/v1/questions/count` | Количество вопросов |
| GET | `/api/v1/questions/count-unanswered` | Неотвеченные |
| PATCH | `/api/v1/questions` | Ответить |

### Sales (Продажи)
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/api/v1/supplier/sales` | Отчет о продажах |
| GET | `/api/v1/supplier/orders` | Отчет о заказах |
| GET | `/api/v1/supplier/stocks` | Отчет об остатках |
| GET | `/api/v1/supplier/reportDetailByPeriod` | Детальный отчет |

---

## Интеграция с основным проектом

Mock API можно использовать для разработки Этапа 2:

### В WB Service

```python
# backend/services/wb_service.py

class WildberriesService:
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        # Для разработки используем Mock API
        self.base_url = base_url or "http://localhost:8001"
        # Для продакшена: "https://suppliers-api.wildberries.ru"
    
    async def get_products(self) -> List[Product]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/content/v2/get/cards/list",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
```

### В Settings

```python
# backend/config/settings.py

class Settings(BaseSettings):
    # ...
    wb_api_url: str = Field(
        default="http://localhost:8001",  # Mock API
        description="Wildberries API base URL"
    )
    # Для продакшена: "https://suppliers-api.wildberries.ru"
```

---

## Переключение между Mock и Real API

```python
# В .env файле:

# Для разработки (Mock API)
WB_API_URL=http://localhost:8001
WB_API_KEY=test-api-key-12345

# Для продакшена (Real API)
# WB_API_URL=https://suppliers-api.wildberries.ru
# WB_API_KEY=your-real-api-key
```

Просто переключаем переменные окружения!

---

## Статистика

| Метрика | Значение |
|---------|----------|
| **Endpoints** | 30+ |
| **Models** | 20+ |
| **Тестовых товаров** | 50 |
| **Тестовых отзывов** | 100 |
| **Тестовых вопросов** | 50 |
| **Тестовых продаж** | 200 |
| **Строк кода** | ~1500 |

---

## Преимущества Mock API

### ✅ Для разработки:
- Не нужен доступ к реальному кабинету продавца
- Быстрая разработка без ограничений API
- Контролируемые тестовые данные
- Возможность тестировать edge cases

### ✅ Для тестирования:
- Детерминированные данные
- Имитация ошибок и edge cases
- Проверка обработки rate limiting
- Unit и integration тесты

### ✅ Для демо:
- Работающая демонстрация без реального API
- Быстрые ответы (нет сетевых задержек)
- Полный контроль над данными

---

## Следующие шаги

Теперь можно начинать **Этап 2: Интеграция с Wildberries**:

1. ✅ Mock API готов
2. 🔜 Создать WB Service (использует Mock API)
3. 🔜 Создать модели данных
4. 🔜 Создать API endpoints
5. 🔜 Позже переключиться на Real API

---

## Документация

- ✅ `backend/mock_api/README.md` — основная документация
- ✅ `backend/mock_api/EXAMPLES.md` — примеры использования
- ✅ `http://localhost:8001/docs` — Swagger UI
- ✅ `http://localhost:8001/redoc` — ReDoc

---

## 🎉 Готово!

Mock API полностью готов к использованию для разработки AI Marketplace Assistant!

**Можно начинать Этап 2 без доступа к реальному WB API!** 🚀

---

**Дата:** 9 марта 2026  
**Версия:** 1.0.0  
**Статус:** ✅ ГОТОВО К ИСПОЛЬЗОВАНИЮ
