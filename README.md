# О проекте

Цель проекта - автоматическая генерация полигональных сеток представительных объемов заданной структуры с гибкой настройкой параметров. Для интеграции с расчетными системами на основе метода конечных элементов модуль генерации сеток выделен в микросервис, но возможно использование также и в виде CLI-утилиты

# Установка зависимостей

```bash
pip install -r requirements.txt
```

Для запуска через Procfile:

```bash
gem install foreman
```

Также для работы celery нужен Redis. Устанавливать по [гайду из документации Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)

# Использование

## CLI-утилита

```bash
python generate_mesh.py [опции]
```

### ⚙️ Основные параметры:

| Параметр               | Описание                                      | По умолчанию            |
|------------------------|-----------------------------------------------|--------------------------|
| `--r-root`             | Радиус корня                                  | `0.5`                    |
| `--h-root`             | Высота корня                                  | `4.0`                    |
| `--r-branch`           | Радиус ветвей                                 | `0.4`                    |
| `--h-branch`           | Высота ветвей                                 | `3.0`                    |
| `--num-branches`       | Кол-во ветвей                                 | `4`                      |
| `--angle`              | Угол между ветвями (в градусах)               | `30`                     |
| `--mesh-size`          | Размер элементов сетки                        | `1.0`                    |
| `--output`             | Имя выходного `.msh` файла                    | `branch_element.msh`     |
| `--export-formats`     | Экспорт в доп. форматы (`stl,obj,vtk,...`)    | _не указано_             |
| `--no-gui`             | Не запускать GUI Gmsh                         | _false_                  |
| `--log-file`           | Путь к лог-файлу                              | _не указано_             |
| `--config`             | Конфигурационный файл `.yaml` или `.json`    | _не указано_             |


### 📝 Пример конфигурации (config.yaml)

```yaml
r_root: 0.6
h_root: 5.0
num_branches: 6
angle: 25
mesh_size: 0.8
output: "cool_branch.msh"
export_formats: "stl,obj"
no_gui: true
log_file: "generation.log"
```

### 🧪 Примеры запуска

#### Запуск с параметрами из командной строки:
```bash
python generate_mesh.py --r-root 0.6 --num-branches 6 --angle 45 --no-gui --output result.msh
```

#### Запуск с конфигурационного файла:
```bash
python generate_mesh.py --config config.yaml
```

## Микросервис

> `localhost:8080/docs` - API-документация HTTP-сервиса для генерации сеток

В проекте используется аутентификация по токену в хедере API-KEY, поэтому для тестов необходимо добавлять этот токен во все запросы.
Корректное значение задается переменной окружения API_KEY, поэтому её необходимо устанавливать перед запуском сервера

### Запуск через Docker

Можно просто запустить docker-compose со стандартными настройками. Корректный API-KEY в этом случае `123` (поменять для production !)
```bash
docker-compose up
```

При необходимости проверить webhook, можно отдельно запустить test_webhook сервер(тут процесс через Docker не налажен пока):

```bash
python -m uvicorn test_webhook:app --reload --port=8001
```

Тогда в запросе `/generate` нужно будет указывать webhook_url: http://localhost:8001/webhook

### Запуск без Docker

#### Запуск через foreman

Если установлен `foreman`, можно запускать все сервисы через

```bash
API_KEY=<ваш ключ> foreman start
```

#### Запуск команд вручную
Альтернативно, можно запускать их по одному:

1. Запуск основного сервера

```bash
API_KEY=<ваш ключ> python -m uvicorn main:app --reload
```

2. Запуск celery

```bash
celery -A tasks.celery_app worker --loglevel=info
```

3. (Опционально) запуск сервера для тестового веб-хука на порту 8001

```bash
python -m uvicorn test_webhook:app --reload --port=8001
```

