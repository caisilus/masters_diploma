FROM python:3.11-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libglu-dev \
    libxrender1 \
    libxext6 \
    libxcursor1 \
    libxft2 \
    libxinerama1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Задаем переменные окружения (если нужно, их можно переопределить через compose)
ENV ENV=production

# По умолчанию запускаем uvicorn для веб-сервиса
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
