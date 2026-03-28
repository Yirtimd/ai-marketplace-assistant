# Wildberries Mock API — Примеры использования

## Базовый URL

```
http://localhost:8001
```

## Авторизация

Все запросы требуют заголовок авторизации:

```
Authorization: Bearer test-api-key-12345
```

---

## Товары (Products)

### Получить список товаров

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/content/v2/get/cards/list?limit=10&offset=0"
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
      "imtID": 20001,
      "vendorCode": "ART00001",
      "brand": "Nike",
      "title": "Nike Кроссовки 1",
      "description": "Качественный кроссовки от бренда Nike...",
      "sizes": [...],
      "photos": [...],
      "characteristics": [...]
    }
  ]
}
```

### Получить товар по ID

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/content/v2/cards/10001"
```

### Получить категории

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/content/v2/object/parent/all"
```

### Получить предметы

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/content/v2/object/all"
```

### Получить характеристики предмета

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/content/v2/object/charcs/101"
```

### Получить бренды

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/content/v2/directory/brands"
```

---

## Отзывы (Feedbacks)

### Получить список отзывов

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/feedbacks?take=10&skip=0"
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
      "isAnswered": false
    }
  ],
  "countUnanswered": 42,
  "countArchive": 5
}
```

### Получить только неотвеченные отзывы

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/feedbacks?is_answered=false"
```

### Получить отзыв по ID

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/feedback?id=feedback-000001"
```

### Ответить на отзыв

```bash
curl -X POST \
  -H "Authorization: Bearer test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "feedback-000001",
    "text": "Спасибо за отзыв! Рады, что вам понравилось!"
  }' \
  "http://localhost:8001/api/v1/feedbacks/answer"
```

### Получить количество неотвеченных отзывов

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/feedbacks/count-unanswered"
```

---

## Вопросы (Questions)

### Получить список вопросов

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/questions?take=10&skip=0"
```

### Получить только неотвеченные вопросы

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/questions?is_answered=false"
```

### Ответить на вопрос

```bash
curl -X PATCH \
  -H "Authorization: Bearer test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "question-000001",
    "text": "Да, размер соответствует стандартной сетке."
  }' \
  "http://localhost:8001/api/v1/questions"
```

### Получить новые отзывы и вопросы

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/new-feedbacks-questions"
```

---

## Продажи (Sales)

### Получить отчет о продажах

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/supplier/sales?limit=10"
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
      "brand": "Nike"
    }
  ],
  "total": 200
}
```

### Получить продажи за период

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/supplier/sales?dateFrom=2026-03-01T00:00:00&dateTo=2026-03-09T23:59:59"
```

### Получить заказы

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/supplier/orders?limit=10"
```

### Получить остатки

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  "http://localhost:8001/api/v1/supplier/stocks"
```

**Response:**
```json
{
  "stocks": [
    {
      "supplierArticle": "ART00001",
      "techSize": "42",
      "barcode": "SKU1",
      "quantity": 25,
      "warehouseName": "Коледино",
      "nmId": 10001,
      "Price": 5000,
      "Discount": 20
    }
  ],
  "total": 350
}
```

---

## Python примеры

### Использование с requests

```python
import requests

BASE_URL = "http://localhost:8001"
API_KEY = "test-api-key-12345"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Получить товары
response = requests.get(
    f"{BASE_URL}/content/v2/get/cards/list",
    headers=headers,
    params={"limit": 10}
)
products = response.json()

# Получить отзывы
response = requests.get(
    f"{BASE_URL}/api/v1/feedbacks",
    headers=headers,
    params={"is_answered": False, "take": 20}
)
feedbacks = response.json()

# Ответить на отзыв
response = requests.post(
    f"{BASE_URL}/api/v1/feedbacks/answer",
    headers=headers,
    json={
        "id": "feedback-000001",
        "text": "Спасибо за отзыв!"
    }
)

# Получить продажи
response = requests.get(
    f"{BASE_URL}/api/v1/supplier/sales",
    headers=headers,
    params={"limit": 100}
)
sales = response.json()
```

### Использование с httpx (async)

```python
import httpx
import asyncio

async def fetch_data():
    BASE_URL = "http://localhost:8001"
    API_KEY = "test-api-key-12345"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        # Получить товары
        response = await client.get(
            f"{BASE_URL}/content/v2/get/cards/list",
            headers=headers
        )
        products = response.json()
        
        # Получить отзывы
        response = await client.get(
            f"{BASE_URL}/api/v1/feedbacks",
            headers=headers
        )
        feedbacks = response.json()
        
        return products, feedbacks

products, feedbacks = asyncio.run(fetch_data())
```

---

## Rate Limiting

Mock API имитирует rate limiting Wildberries:

- **Лимит:** 3 запроса в секунду
- **Burst:** 6 запросов

При превышении лимита возвращается ошибка `429 Too Many Requests`.

---

## Ошибки

### 401 Unauthorized

```json
{
  "error": true,
  "errorText": "Authorization header required"
}
```

### 404 Not Found

```json
{
  "error": true,
  "errorText": "Product not found",
  "data": {}
}
```

### 429 Too Many Requests

```json
{
  "error": true,
  "errorText": "Rate limit exceeded. Max 3 requests per second."
}
```

---

## Тестовые данные

Mock API содержит:

- **50 товаров** различных категорий
- **100 отзывов** (положительные, отрицательные, нейтральные)
- **50 вопросов** от покупателей
- **200 продаж** за последние 90 дней
- **150 заказов**
- **350+ записей остатков** по всем товарам и размерам

---

## Swagger UI

Полная интерактивная документация доступна по адресу:

```
http://localhost:8001/docs
```

В Swagger UI можно:
- Просмотреть все доступные endpoints
- Протестировать запросы
- Посмотреть примеры ответов
- Скачать OpenAPI схему
