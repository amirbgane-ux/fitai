# Используем стабильный Python 3.11
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Стартовый комманд
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
