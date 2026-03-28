# 🧪 Руководство по тестированию — Этапы 1 и 2

## Обзор

После реализации Этапов 1 и 2 у нас есть:
- ✅ Backend инфраструктура (FastAPI, PostgreSQL, Redis)
- ✅ Mock API для Wildberries
- ✅ WildberriesService для работы с API
- ✅ 14 API endpoints для работы с данными WB

Давайте всё протестируем!

---

## Подготовка к тестированию

### 1. Проверить структуру проекта

```bash
cd ~/Desktop/sl_AI_ve/ai-marketplace-assistant/backend
ls -la
```

Должны увидеть:
```
api/
config/
database/
services/
schemas/
mock_api/
main.py
requirements.txt
.env.example
```

### 2. Создать .env файл

```bash
cd backend
cp .env.example .env
```

Открыть `.env` и настроить:
```bash
# Для тестирования используем Mock API
WB_API_URL=http://localhost:8001
WB_API_KEY=test-api-key-12345

# PostgreSQL (можно оставить по умолчанию)
DATABASE_URL=postgresql://ai_marketplace:ai_marketplace_password@localhost:5432/ai_marketplace

# Redis (можно оставить по умолчанию)
REDIS_URL=redis://localhost:6379/0

# Secret key (сгенерировать или оставить тестовый)
SECRET_KEY=test-secret-key-for-development-only
```

### 3. Установить зависимости

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Это займет несколько минут.

---

## Тест 1: Запуск инфраструктуры (Docker)

### Запустить PostgreSQL и Redis

```bash
cd backend
docker-compose up -d
```

### Проверить что контейнеры запущены

```bash
docker ps
```

Должны увидеть:
```
ai_marketplace_postgres
ai_marketplace_redis
```

### Проверить подключение к PostgreSQL

```bash
docker exec -it ai_marketplace_postgres psql -U ai_marketplace -d ai_marketplace
```

В psql выполнить:
```sql
\l  -- список баз данных
\q  -- выход
```

### Проверить подключение к Redis

```bash
docker exec -it ai_marketplace_redis redis-cli ping
```

Должно вернуть: `PONG`

✅ **Инфраструктура работает!**

---

## Тест 2: Запуск Mock API

### Открыть первый терминал

```bash
cd backend/mock_api
source ../venv/bin/activate
./start.sh
```

Или запустить напрямую:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Проверить Mock API

В браузере открыть:
```
http://localhost:8001/docs
```

Должна открыться Swagger UI с endpoints Mock API.

### Тестовый запрос к Mock API

В другом терминале:
```bash
curl http://localhost:8001/health
```

Ответ:
```json
{
  "status": "healthy",
  "products": "available",
  "feedbacks": "available",
  "sales": "available"
}
```

### Получить товары из Mock API

```bash
curl -H "Authorization: Bearer test-api-key-12345" \
  http://localhost:8001/content/v2/get/cards/list?limit=5
```

Должны получить список из 5 товаров!

✅ **Mock API работает!**

---

## Тест 3: Запуск основного Backend API

### Открыть второй терминал

```bash
cd backend
source venv/bin/activate
./start.sh
```

Или запустить напрямую:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Проверить логи запуска

Должны увидеть:
```
INFO:     Starting AI Marketplace Assistant backend
INFO:     Version: 0.1.0
INFO:     Debug mode: False
INFO:     Database initialized
INFO:     Redis initialized
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Открыть Swagger UI

В браузере:
```
http://localhost:8000/docs
```

Должны увидеть все endpoints с тегами:
- v1
- Products
- Feedbacks & Questions
- Sales & Reports

✅ **Backend API запущен!**

---

## Тест 4: Базовые endpoints

### Тест Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "0.1.0"
}
```

### Тест API Root

```bash
curl http://localhost:8000/api/v1/
```

Ответ:
```json
{
  "name": "AI Marketplace Assistant",
  "version": "0.1.0",
  "api_version": "v1",
  "status": "running"
}
```

✅ **Базовые endpoints работают!**

---

## Тест 5: Products Endpoints

### Получить список товаров

```bash
curl http://localhost:8000/api/v1/products/?limit=5
```

**Что проверить:**
- Статус: 200 OK
- Есть поле `cursor` с информацией о пагинации
- Есть поле `cards` со списком товаров
- Каждый товар имеет: nmID, brand, title, description, sizes, photos

### Получить конкретный товар

```bash
curl http://localhost:8000/api/v1/products/10001
```

**Что проверить:**
- Статус: 200 OK
- Возвращается один товар с nmID=10001
- Есть все поля товара

### Получить категории

```bash
curl http://localhost:8000/api/v1/products/reference/categories
```

**Что проверить:**
- Возвращается список категорий
- Каждая имеет: id, name, parentID

### Получить бренды

```bash
curl http://localhost:8000/api/v1/products/reference/brands
```

**Что проверить:**
- Возвращается список брендов
- Есть Nike, Adidas, Samsung и другие

### Фильтр брендов по имени

```bash
curl http://localhost:8000/api/v1/products/reference/brands?name=Nike
```

**Что проверить:**
- Возвращаются только бренды с "Nike" в названии

✅ **Products endpoints работают!**

---

## Тест 6: Feedbacks Endpoints

### Получить список отзывов

```bash
curl http://localhost:8000/api/v1/feedbacks/?take=5
```

**Что проверить:**
- Статус: 200 OK
- Есть поля: feedbacks, countUnanswered, countArchive
- В feedbacks есть отзывы с полями: id, productValuation, text, userName

### Получить только неотвеченные отзывы

```bash
curl http://localhost:8000/api/v1/feedbacks/?is_answered=false&take=10
```

**Что проверить:**
- Все отзывы имеют `isAnswered: false`
- Количество соответствует `countUnanswered`

### Получить конкретный отзыв

```bash
curl http://localhost:8000/api/v1/feedbacks/feedback-000001
```

**Что проверить:**
- Возвращается отзыв с id="feedback-000001"

### Ответить на отзыв

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"id": "feedback-000001", "text": "Спасибо за ваш отзыв! Рады что вам понравилось!"}' \
  http://localhost:8000/api/v1/feedbacks/feedback-000001/answer
```

**Что проверить:**
- Статус: 200 OK
- Ответ: `{"success": true, "data": {...}}`

### Получить статистику неотвеченных

```bash
curl http://localhost:8000/api/v1/feedbacks/stats/unanswered
```

**Что проверить:**
- Возвращается `{"countUnanswered": N}`

✅ **Feedbacks endpoints работают!**

---

## Тест 7: Questions Endpoints

### Получить список вопросов

```bash
curl http://localhost:8000/api/v1/feedbacks/questions?take=5
```

**Что проверить:**
- Возвращается список вопросов
- Есть поля: id, text, userName, isAnswered

### Получить неотвеченные вопросы

```bash
curl http://localhost:8000/api/v1/feedbacks/questions?is_answered=false&take=10
```

**Что проверить:**
- Все вопросы имеют `isAnswered: false`

### Ответить на вопрос

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"id": "question-000001", "text": "Да, товар соответствует размерной сетке."}' \
  http://localhost:8000/api/v1/feedbacks/questions/question-000001/answer
```

**Что проверить:**
- Статус: 200 OK
- Успешный ответ

### Получить статистику новых

```bash
curl http://localhost:8000/api/v1/feedbacks/stats/new
```

**Что проверить:**
- Возвращаются счетчики новых отзывов и вопросов

✅ **Questions endpoints работают!**

---

## Тест 8: Sales Endpoints

### Получить отчет о продажах

```bash
curl http://localhost:8000/api/v1/sales/?limit=10
```

**Что проверить:**
- Возвращается список продаж
- Каждая продажа имеет: saleID, orderID, date, totalPrice, nmId, brand

### Получить продажи за период

```bash
curl "http://localhost:8000/api/v1/sales/?date_from=2026-03-01T00:00:00&date_to=2026-03-09T23:59:59&limit=50"
```

**Что проверить:**
- Все продажи в указанном периоде
- Даты находятся между date_from и date_to

### Получить заказы

```bash
curl http://localhost:8000/api/v1/sales/orders?limit=10
```

**Что проверить:**
- Возвращается список заказов
- Есть поля: orderID, date, nmId, isCancel

### Получить остатки

```bash
curl http://localhost:8000/api/v1/sales/stocks
```

**Что проверить:**
- Возвращается список остатков
- Каждый имеет: nmId, quantity, warehouseName, Price

✅ **Sales endpoints работают!**

---

## Тест 9: Swagger UI интерактивное тестирование

### Открыть Swagger UI

```
http://localhost:8000/docs
```

### Протестировать через интерфейс

1. **Products - GET /api/v1/products/**
   - Нажать "Try it out"
   - Установить limit=5
   - Нажать "Execute"
   - Проверить Response body

2. **Feedbacks - GET /api/v1/feedbacks/**
   - "Try it out"
   - Установить is_answered=false, take=10
   - "Execute"
   - Проверить список неотвеченных

3. **Feedbacks - POST /api/v1/feedbacks/{feedback_id}/answer**
   - "Try it out"
   - feedback_id: "feedback-000001"
   - Request body:
     ```json
     {
       "id": "feedback-000001",
       "text": "Спасибо за ваш отзыв!"
     }
     ```
   - "Execute"
   - Проверить успешный ответ

4. **Sales - GET /api/v1/sales/**
   - "Try it out"
   - limit=20
   - "Execute"
   - Проверить список продаж

✅ **Swagger UI работает!**

---

## Тест 10: Python скрипт

Создайте файл `test_api.py`:

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"

async def test_all_endpoints():
    async with httpx.AsyncClient() as client:
        print("🧪 Тестирование API endpoints...\n")
        
        # Health check
        print("1️⃣ Health Check")
        response = await client.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
        
        # Products
        print("2️⃣ Получение товаров")
        response = await client.get(f"{BASE_URL}/products/", params={"limit": 5})
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Товаров получено: {len(data['cards'])}\n")
        
        # Feedbacks
        print("3️⃣ Получение отзывов")
        response = await client.get(
            f"{BASE_URL}/feedbacks/",
            params={"is_answered": False, "take": 10}
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Отзывов получено: {len(data['feedbacks'])}")
        print(f"   Неотвеченных: {data['countUnanswered']}\n")
        
        # Sales
        print("4️⃣ Получение продаж")
        response = await client.get(f"{BASE_URL}/sales/", params={"limit": 50})
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Продаж получено: {len(data['sales'])}")
        print(f"   Всего: {data['total']}\n")
        
        # Stocks
        print("5️⃣ Получение остатков")
        response = await client.get(f"{BASE_URL}/sales/stocks")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Позиций: {len(data['stocks'])}")
        print(f"   Всего: {data['total']}\n")
        
        print("✅ Все тесты пройдены успешно!")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
```

Запустить:
```bash
cd backend
source venv/bin/activate
python test_api.py
```

✅ **Python скрипт работает!**

---

## Тест 11: Проверка логов

### Backend логи

В терминале где запущен backend, проверить что логи выводятся:
```
INFO: Getting products: limit=5, offset=0
INFO: Getting feedbacks: is_answered=False, take=10, skip=0
INFO: Getting sales: date_from=None, date_to=None, limit=50
```

### Mock API логи

В терминале где запущен Mock API:
```
INFO: 200 GET /content/v2/get/cards/list
INFO: 200 GET /api/v1/feedbacks
INFO: 200 GET /api/v1/supplier/sales
```

✅ **Логирование работает!**

---

## Тест 12: Переключение на Real API (опционально)

Если у вас есть реальный API ключ от Wildberries:

### Изменить .env

```bash
# Закомментировать Mock API
# WB_API_URL=http://localhost:8001
# WB_API_KEY=test-api-key-12345

# Раскомментировать Real API
WB_API_URL=https://suppliers-api.wildberries.ru
WB_API_KEY=your-real-api-key-here
```

### Перезапустить backend

```bash
# Ctrl+C в терминале с backend
# Запустить снова
./start.sh
```

### Протестировать с реальными данными

```bash
curl http://localhost:8000/api/v1/products/?limit=5
```

Должны получить РЕАЛЬНЫЕ товары из вашего магазина!

✅ **Переключение работает!**

---

## Чеклист тестирования

- [ ] Docker контейнеры запущены (PostgreSQL, Redis)
- [ ] Mock API запущен на порту 8001
- [ ] Backend API запущен на порту 8000
- [ ] Health check возвращает "healthy"
- [ ] Products endpoints работают (5 endpoints)
- [ ] Feedbacks endpoints работают (7 endpoints)
- [ ] Sales endpoints работают (3 endpoints)
- [ ] Swagger UI доступен и работает
- [ ] Python скрипт успешно выполняется
- [ ] Логи корректно выводятся
- [ ] Переключение на Real API работает (опционально)

---

## Что делать если что-то не работает

### Проблема: Docker контейнеры не запускаются

```bash
# Проверить логи
docker-compose logs postgres
docker-compose logs redis

# Пересоздать контейнеры
docker-compose down
docker-compose up -d
```

### Проблема: Backend не подключается к БД

```bash
# Проверить DATABASE_URL в .env
# Убедиться что порт 5432 не занят
lsof -i :5432

# Проверить подключение вручную
docker exec -it ai_marketplace_postgres psql -U ai_marketplace
```

### Проблема: Mock API не отвечает

```bash
# Проверить что порт 8001 не занят
lsof -i :8001

# Запустить с debug логами
uvicorn main:app --reload --host 0.0.0.0 --port 8001 --log-level debug
```

### Проблема: Backend возвращает 500

- Проверить логи в терминале
- Проверить что Mock API запущен
- Проверить WB_API_URL в .env

### Проблема: Импорты не работают

```bash
# Переустановить зависимости
pip install --upgrade -r requirements.txt

# Проверить PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/ai-marketplace-assistant"
```

---

## Итоги тестирования

После прохождения всех тестов у вас должно быть:

✅ Работающая инфраструктура (PostgreSQL, Redis)  
✅ Mock API с тестовыми данными  
✅ Backend API с 14 endpoints  
✅ WildberriesService интегрирован  
✅ Swagger UI документация  
✅ Возможность переключения на Real API  

**Система готова к Этапу 3! 🚀**

---

## Следующие шаги

После успешного тестирования можно переходить к:

**Этап 3 — Модель данных системы:**
- Создание SQLAlchemy моделей
- Настройка Alembic миграций
- CRUD операции
- Синхронизация данных из WB API в БД

---

**Удачи в тестировании! 🧪**
