# 🚀 Быстрый старт — Тестирование системы

## Пошаговая инструкция

### Шаг 1: Подготовка

```bash
cd ~/Desktop/sl_AI_ve/ai-marketplace-assistant/backend

# Создать .env файл
cp .env.example .env

# Установить зависимости (если еще не установлены)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 2: Запустить инфраструктуру

```bash
# Запустить PostgreSQL и Redis
docker-compose up -d

# Проверить
docker ps
```

### Шаг 3: Запустить Mock API

**Терминал 1:**
```bash
cd backend/mock_api
source ../venv/bin/activate
./start.sh
```

Должно появиться: `Uvicorn running on http://0.0.0.0:8001`

### Шаг 4: Запустить Backend API

**Терминал 2:**
```bash
cd backend
source venv/bin/activate
./start.sh
```

Должно появиться: `Uvicorn running on http://0.0.0.0:8000`

### Шаг 5: Запустить тесты

**Терминал 3:**
```bash
cd backend
source venv/bin/activate
python test_api.py
```

Должно пройти 13 тестов!

---

## Быстрая проверка через curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Товары (5 штук)
curl http://localhost:8000/api/v1/products/?limit=5

# Отзывы (неотвеченные)
curl http://localhost:8000/api/v1/feedbacks/?is_answered=false&take=10

# Продажи
curl http://localhost:8000/api/v1/sales/?limit=20
```

---

## Swagger UI

Откройте в браузере:
```
http://localhost:8000/docs
```

Интерактивное тестирование всех endpoints!

---

## Что должно работать

✅ 2 endpoints базовых (health, root)  
✅ 5 endpoints товаров  
✅ 7 endpoints отзывов/вопросов  
✅ 3 endpoints продаж  

**Всего: 17 endpoints**

---

## Если что-то не работает

### Mock API не запускается
```bash
# Проверить порт
lsof -i :8001

# Запустить вручную
cd backend/mock_api
uvicorn main:app --reload --port 8001
```

### Backend не запускается
```bash
# Проверить порт
lsof -i :8000

# Проверить .env файл
cat .env | grep WB_API

# Запустить вручную
cd backend
uvicorn backend.main:app --reload --port 8000
```

### Docker не работает
```bash
# Перезапустить
docker-compose down
docker-compose up -d

# Проверить логи
docker-compose logs
```

---

## Готово! 🎉

После успешных тестов переходите к **Этапу 3!**

Полное руководство: `TESTING_GUIDE.md`
