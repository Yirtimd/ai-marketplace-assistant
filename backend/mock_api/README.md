# Wildberries Mock API

Mock API сервер для разработки AI Marketplace Assistant без доступа к реальному API Wildberries.

## Описание

Mock API полностью имитирует поведение реального Wildberries API для разработки и тестирования.

## Возможности

- ✅ Полная имитация Wildberries API
- ✅ Реалистичные тестовые данные
- ✅ Поддержка всех основных endpoints
- ✅ Rate limiting
- ✅ Авторизация по токену
- ✅ Swagger документация

## Категории API

### 1. Работа с товарами
- Создание и управление карточками товаров
- Категории и характеристики
- Медиа файлы
- Цены и скидки
- Управление складами и остатками

### 2. Вопросы и отзывы
- Список отзывов
- Ответы на отзывы
- Вопросы покупателей
- Чаты с покупателями
- Возвраты

### 3. Отчеты
- Статистика продаж
- Отчеты по остаткам
- Финансовые отчеты

### 4. Тарифы
- Информация о комиссиях
- Тарифы доставки

## Запуск

```bash
cd backend/mock_api
uvicorn main:app --reload --port 8001
```

Mock API будет доступен по адресу: http://localhost:8001

Документация: http://localhost:8001/docs

## Использование

### Авторизация

Все запросы требуют заголовок:
```
Authorization: Bearer test-api-key-12345
```

### Примеры запросов

```bash
# Получить список товаров
curl -H "Authorization: Bearer test-api-key-12345" \
  http://localhost:8001/content/v2/get/cards/list

# Получить отзывы
curl -H "Authorization: Bearer test-api-key-12345" \
  http://localhost:8001/api/v1/feedbacks

# Получить статистику продаж
curl -H "Authorization: Bearer test-api-key-12345" \
  http://localhost:8001/api/v1/supplier/sales
```

## Тестовые данные

Mock API возвращает реалистичные тестовые данные для разработки:
- 50+ тестовых товаров
- 100+ отзывов
- 200+ продаж
- Вопросы покупателей
- История заказов

## Структура

```
mock_api/
├── main.py                    # Основное приложение
├── routers/                   # API endpoints
│   ├── products.py           # Товары
│   ├── feedbacks.py          # Отзывы
│   ├── sales.py              # Продажи
│   ├── stocks.py             # Остатки
│   └── tariffs.py            # Тарифы
├── data/                      # Тестовые данные
│   ├── products.py
│   ├── feedbacks.py
│   └── sales.py
└── models/                    # Pydantic модели
    ├── product.py
    ├── feedback.py
    └── sale.py
```
