# Этап 2 — Интеграция с Wildberries — Примеры использования

## Запуск системы

### 1. Запустить Mock API (для разработки)

```bash
cd backend/mock_api
./start.sh
```

Mock API будет доступен на `http://localhost:8001`

### 2. Запустить основное приложение

```bash
cd backend
./start.sh
```

Основное API будет доступно на `http://localhost:8000`

---

## Примеры использования API

### Базовые настройки

```bash
BASE_URL="http://localhost:8000"
API_VERSION="/api/v1"
```

---

## Товары (Products)

### Получить список товаров

```bash
curl http://localhost:8000/api/v1/products/?limit=10
```

**Response:**
```json
{
  "cursor": {
    "total": 50,
    "offset": 0,
    "limit": 10
  },
  "cards": [
    {
      "nmID": 10001,
      "vendorCode": "ART00001",
      "brand": "Nike",
      "title": "Nike Кроссовки 1",
      "description": "Качественный кроссовки от бренда Nike...",
      "subjectName": "Кроссовки",
      "sizes": [...],
      "photos": [...],
      "characteristics": [...]
    }
  ]
}
```

### Получить товар по ID

```bash
curl http://localhost:8000/api/v1/products/10001
```

### Получить категории

```bash
curl http://localhost:8000/api/v1/products/reference/categories
```

### Получить бренды

```bash
curl http://localhost:8000/api/v1/products/reference/brands?name=Nike
```

---

## Отзывы (Feedbacks)

### Получить список отзывов

```bash
curl http://localhost:8000/api/v1/feedbacks/?take=10
```

### Получить только неотвеченные отзывы

```bash
curl http://localhost:8000/api/v1/feedbacks/?is_answered=false&take=20
```

**Response:**
```json
{
  "data": {"total": 100},
  "feedbacks": [
    {
      "id": "feedback-000001",
      "nmId": 10001,
      "productName": "Nike Кроссовки 1",
      "productValuation": 5,
      "text": "Отличный товар! Очень доволен покупкой.",
      "userName": "Покупатель1",
      "createdDate": "2026-03-09T10:00:00",
      "isAnswered": false,
      "wasViewed": true
    }
  ],
  "countUnanswered": 42,
  "countArchive": 5
}
```

### Ответить на отзыв

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"id": "feedback-000001", "text": "Спасибо за отзыв!"}' \
  http://localhost:8000/api/v1/feedbacks/feedback-000001/answer
```

### Получить количество неотвеченных

```bash
curl http://localhost:8000/api/v1/feedbacks/stats/unanswered
```

---

## Вопросы (Questions)

### Получить список вопросов

```bash
curl http://localhost:8000/api/v1/feedbacks/questions?take=10
```

### Ответить на вопрос

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"id": "question-000001", "text": "Да, размер соответствует."}' \
  http://localhost:8000/api/v1/feedbacks/questions/question-000001/answer
```

### Получить статистику новых

```bash
curl http://localhost:8000/api/v1/feedbacks/stats/new
```

---

## Продажи (Sales)

### Получить отчет о продажах

```bash
curl http://localhost:8000/api/v1/sales/?limit=100
```

**Response:**
```json
{
  "sales": [
    {
      "saleID": "S0000000001",
      "orderID": "O0000000001",
      "date": "2026-03-09T10:00:00",
      "supplierArticle": "ART00001",
      "techSize": "42",
      "totalPrice": 5000,
      "discountPercent": 20,
      "warehouseName": "Коледино",
      "nmId": 10001,
      "brand": "Nike",
      "forPay": 4000,
      "finishedPrice": 4000
    }
  ],
  "total": 200
}
```

### Получить продажи за период

```bash
curl "http://localhost:8000/api/v1/sales/?date_from=2026-03-01T00:00:00&date_to=2026-03-09T23:59:59"
```

### Получить заказы

```bash
curl http://localhost:8000/api/v1/sales/orders?limit=50
```

### Получить остатки

```bash
curl http://localhost:8000/api/v1/sales/stocks
```

---

## Python примеры

### Асинхронный клиент (httpx)

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient() as client:
        # Получить товары
        response = await client.get(f"{BASE_URL}/products/", params={"limit": 10})
        products = response.json()
        print(f"Товаров: {len(products['cards'])}")
        
        # Получить отзывы
        response = await client.get(
            f"{BASE_URL}/feedbacks/",
            params={"is_answered": False, "take": 20}
        )
        feedbacks = response.json()
        print(f"Неотвеченных отзывов: {feedbacks['countUnanswered']}")
        
        # Ответить на отзыв
        if feedbacks['feedbacks']:
            feedback_id = feedbacks['feedbacks'][0]['id']
            response = await client.post(
                f"{BASE_URL}/feedbacks/{feedback_id}/answer",
                json={"id": feedback_id, "text": "Спасибо за отзыв!"}
            )
            print(f"Ответ отправлен: {response.json()}")
        
        # Получить продажи
        response = await client.get(f"{BASE_URL}/sales/", params={"limit": 100})
        sales = response.json()
        print(f"Продаж: {sales['total']}")

asyncio.run(main())
```

### Синхронный клиент (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Получить товары
response = requests.get(f"{BASE_URL}/products/", params={"limit": 10})
products = response.json()

# Получить отзывы
response = requests.get(
    f"{BASE_URL}/feedbacks/",
    params={"is_answered": False}
)
feedbacks = response.json()

# Получить продажи за последние 7 дней
from datetime import datetime, timedelta

date_from = (datetime.now() - timedelta(days=7)).isoformat()
date_to = datetime.now().isoformat()

response = requests.get(
    f"{BASE_URL}/sales/",
    params={"date_from": date_from, "date_to": date_to}
)
sales = response.json()
```

---

## Использование в коде проекта

### В сервисах

```python
from backend.services import get_wb_service

wb = get_wb_service()

# Получить товары
products = await wb.get_products(limit=10)

# Получить отзывы
feedbacks = await wb.get_feedbacks(is_answered=False, take=20)

# Ответить на отзыв
await wb.answer_feedback("feedback-000001", "Спасибо!")

# Получить продажи
sales = await wb.get_sales(limit=100)
```

### В API endpoints

```python
from fastapi import Depends
from backend.config.dependencies import get_wb_service
from backend.services import WildberriesService

@app.get("/my-products")
async def my_products(wb: WildberriesService = Depends(get_wb_service)):
    products = await wb.get_products(limit=50)
    return products
```

---

## Переключение между Mock и Real API

### В `.env` файле:

```bash
# Для разработки (Mock API)
WB_API_URL=http://localhost:8001
WB_API_KEY=test-api-key-12345

# Для продакшена (Real API)
# WB_API_URL=https://suppliers-api.wildberries.ru
# WB_API_KEY=your-real-api-key-here
```

Просто раскомментируйте нужные строки!

---

## Swagger UI

Полная интерактивная документация доступна по адресу:

```
http://localhost:8000/docs
```

В Swagger UI можно:
- Просмотреть все endpoints
- Протестировать запросы
- Посмотреть примеры ответов
- Скачать OpenAPI схему

---

## Доступные endpoints

| Method | Endpoint | Описание |
|--------|----------|----------|
| **Products** |
| GET | `/api/v1/products/` | Список товаров |
| GET | `/api/v1/products/{nm_id}` | Товар по ID |
| GET | `/api/v1/products/reference/categories` | Категории |
| GET | `/api/v1/products/reference/subjects` | Предметы |
| GET | `/api/v1/products/reference/brands` | Бренды |
| **Feedbacks** |
| GET | `/api/v1/feedbacks/` | Список отзывов |
| GET | `/api/v1/feedbacks/{id}` | Отзыв по ID |
| POST | `/api/v1/feedbacks/{id}/answer` | Ответить на отзыв |
| GET | `/api/v1/feedbacks/stats/unanswered` | Неотвеченные |
| GET | `/api/v1/feedbacks/questions` | Список вопросов |
| POST | `/api/v1/feedbacks/questions/{id}/answer` | Ответить на вопрос |
| GET | `/api/v1/feedbacks/stats/new` | Статистика новых |
| **Sales** |
| GET | `/api/v1/sales/` | Отчет о продажах |
| GET | `/api/v1/sales/orders` | Отчет о заказах |
| GET | `/api/v1/sales/stocks` | Отчет об остатках |

---

## Тестирование

```bash
# Запустить Mock API
cd backend/mock_api
./start.sh

# В другом терминале запустить основное приложение
cd backend
./start.sh

# Протестировать endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/products/?limit=5
curl http://localhost:8000/api/v1/feedbacks/?take=5
curl http://localhost:8000/api/v1/sales/?limit=10
```

---

## Готово! 🎉

Этап 2 завершен! Теперь система может:
- ✅ Получать товары из WB
- ✅ Получать отзывы и вопросы
- ✅ Отвечать на отзывы
- ✅ Получать продажи и остатки
- ✅ Работать с Mock API для разработки
- ✅ Легко переключаться на Real API
