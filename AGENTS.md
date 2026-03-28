# AGENTS.md

# Архитектура AI агентов

Этот файл описывает систему агентов проекта AI Marketplace Assistant.

Агенты — это специализированные компоненты, которые выполняют отдельные задачи внутри системы.

Каждый агент отвечает за конкретную область.

Агенты используются внутри LangGraph workflow.

Текущий статус: **Этап 6 реализован**.

Базовые stateless-агенты созданы в `backend/agents/` и готовы для использования в workflow.

---

# Основные принципы архитектуры агентов

1. Агенты должны быть stateless.

Агент не должен хранить состояние внутри себя.

Все состояние хранится в базе данных.

---

2. Агенты выполняют только одну доменную задачу.

Каждый агент должен иметь четкую область ответственности.

---

3. Агенты вызываются через orchestrator или workflow.

Агенты не взаимодействуют напрямую друг с другом.

---

# Основные агенты системы

---

# Analytics Agent

Файл:

```
agents/analytics_agent.py
```

Назначение:

анализ данных магазина.

Основные задачи:

* анализ продаж
* выявление трендов
* анализ динамики
* анализ конкурентов

Основные функции:

analyze_sales()

detect_trends()

analyze_competitors()

Выходные данные:

* аналитический отчет
* рекомендации

---

# Inventory Agent

Файл:

```
agents/inventory_agent.py
```

Назначение:

контроль остатков товаров.

Задачи:

* анализ остатков
* расчет скорости продаж
* прогноз окончания товара

Основные функции:

calculate_sales_velocity()

predict_stock_out()

generate_reorder_recommendation()

Результат:

* уведомление о низком остатке
* рекомендации по заказу

---

# Content Agent

Файл:

```
agents/content_agent.py
```

Назначение:

генерация контента для карточек товаров.

Задачи:

* генерация описаний
* генерация изображений
* генерация видео
* SEO оптимизация

Основные функции:

generate_product_description()

generate_product_images()

generate_product_video()

optimize_seo()

---

# Review Agent

Файл:

```
agents/review_agent.py
```

Назначение:

работа с отзывами покупателей.

Задачи:

* анализ отзывов
* определение тональности
* генерация ответа
* публикация ответа

Основные функции:

analyze_sentiment()

generate_reply()

publish_reply()

---

# Pricing Agent

Файл:

```
agents/pricing_agent.py
```

Назначение:

управление ценами товаров.

Задачи:

* анализ цен конкурентов
* оценка спроса
* рекомендации по цене

Основные функции:

analyze_competitor_prices()

estimate_demand()

recommend_price()

update_price()

---

# Реализация Stage 6

Созданы файлы:

```
backend/agents/analytics_agent.py
backend/agents/inventory_agent.py
backend/agents/review_agent.py
backend/agents/content_agent.py
backend/agents/pricing_agent.py
```

Экспорт агентов:

```
backend/agents/__init__.py
```

Интеграция в workflow:

```
backend/workflows/check_inventory.py
```

`CheckInventoryWorkflow` теперь использует `InventoryAgent` для генерации рекомендаций по пополнению остатков.

---

# Взаимодействие агентов

Агенты не вызывают друг друга напрямую.

Взаимодействие происходит через workflow.

Пример:

```
sales_analysis_workflow
```

внутри workflow:

analytics_agent → pricing_agent

---

# Workflow взаимодействия

Пример workflow:

sales_analysis

```
load_sales_data
↓
analytics_agent
↓
decision_node
↓
pricing_agent
```

---

# Добавление нового агента

Если требуется новая функция:

создается новый агент.

Пример:

advertising_agent
supplier_agent
trend_agent

Новый агент должен:

* иметь четкую область ответственности
* быть stateless
* работать через workflow

---

# Принцип расширяемости

Архитектура должна позволять легко добавлять новых агентов.

Система агентов должна быть:

модульной
расширяемой
независимой

---

# Цель архитектуры агентов

Создать систему, в которой AI может:

анализировать бизнес
принимать решения
выполнять действия

AI должен выступать как **операционный менеджер магазина**.
