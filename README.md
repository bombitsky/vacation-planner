# Планировщик отпуска

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

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

## Настройка Nginx и HTTPS

### Подготовка конфигурации Nginx

1. Отредактируй файл `nginx/nginx.conf` — укажи свой домен в `server_name`
2. Добавь в `docker-compose.yml` в секцию `nginx` проброс порта `443:443` и монтирование папки `./nginx/ssl:/etc/nginx/ssl:ro`

### Получение SSL-сертификата (Let's Encrypt)

1. Останови контейнер Nginx, чтобы освободить порт 80
2. Установи на сервере утилиту `certbot`
3. Выполни получение сертификата для своего домена (в режиме `standalone`)
4. После успешного получения скопируй файлы сертификата в папку проекта:
   - `fullchain.pem` (публичный сертификат)
   - `privkey.pem` (приватный ключ)
   
   Они должны лежать в папке `nginx/ssl/` внутри проекта

### Завершение настройки

1. Обнови `nginx.conf`, добавив секцию для порта 443 с указанием путей к сертификатам:
   - `ssl_certificate /etc/nginx/ssl/fullchain.pem;`
   - `ssl_certificate_key /etc/nginx/ssl/privkey.pem;`
2. Добавь автоматическое перенаправление с HTTP на HTTPS
3. Перезапусти контейнеры
4. Настрой автоматическое обновление сертификатов через планировщик `cron`
      sudo crontab -e
      в конец файла нудно добавить строчку - 0 3 * * * /usr/bin/certbot renew --quiet --post-hook "docker restart vacation-planner-nginx-1"
      ежедневно в 3 часа ночи будет проверка сертификата и обновление если нужно, с последующим перезапуском nginx