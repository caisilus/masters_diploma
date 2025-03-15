# О проекте

Цель проекта - автоматическая генерация полигональных сеток представительных объемов заданной структуры с гибкой настройкой параметров. Для интеграции с расчетными системами на основе метода конечных элементов модуль генерации сеток выделен в микросервис

`localhost:8080/docs` - API-документация HTTP-сервиса для генерации сеток

generation_usage_example.py - скрипт чтобы строить модельки напрямую, минуя http-сервис. Для тестовых целей

# Установка зависимостей

```bash
pip install -r requirements.txt
```

Для запуска через Procfile:

```bash
gem install foreman
```

Также для работы celery нужен Redis. Устанавливать по [гайду из документации Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)

# Запуск проекта

Если установлен `foreman`, можно запускать все сервисы через

```bash
foreman start
```

Альтернативно, можно запускать их по одному:

1. Запуск основного сервера

```bash
python -m uvicorn main:app --reload
```

2. Запуск celery

```bash
celery -A tasks.celery_app worker --loglevel=info
```

3. (Опционально) запуск сервера для тестового веб-хука на порту 8001

```bash
python -m uvicorn test_webhook:app --reload --port=8001
```

