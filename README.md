# Планировщик отпуска

Веб-приложение для планирования отпуска: копилка, чек-лист, варианты туров.

## Запуск через Docker

1. Склонируй репозиторий  
   `git clone https://github.com/bombitsky/vacation-planner.git`

2. Скопируй и настрой `.env`  
   `cp .env.example .env`  
   Отредактируй `.env` — впиши свои `SECRET_KEY` и `POSTGRES_PASSWORD`

3. Запусти контейнеры  
   `docker-compose down`  
   `docker-compose build --no-cache`  
   `docker-compose up -d`

4. Открой в браузере: `http://localhost:5000`

## Локальная разработка (без Docker)

1. Установи PostgreSQL, создай базу `vacation_planner`
2. Установи зависимости: `pip install -r requirements.txt`
3. Создай `.env` с `DATABASE_URL=postgresql://user:pass@localhost:5432/vacation_planner`
4. Запусти: `python vacation_app.py`

## Запуск на VPS (первый раз)

1. Клонируй репозиторий:  
   `git clone https://github.com/bombitsky/vacation-planner.git`

2. Скопируй пример переменных и отредактируй:  
   `cp .env.example .env`  
   Впиши свои `SECRET_KEY` и `POSTGRES_PASSWORD`

3. Запусти контейнеры:  
   `docker compose down`  
   `docker compose build --no-cache`  
   `docker compose up -d`

4. Сайт будет доступен на `http://ip-твоего-сервера:5000`