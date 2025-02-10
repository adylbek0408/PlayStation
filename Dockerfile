# Используем официальный Python образ
FROM python:3.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Создаём директории для статики и медиа
RUN mkdir -p /app/static /app/media

# Открываем порт 8000
EXPOSE 8000

# Команда запуска Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "playstation_backend.wsgi:application"]