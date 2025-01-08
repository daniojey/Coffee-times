# Указываем образ python 
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы в приложение
COPY . /app

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=main.settings
ENV SESSION_COOKIE_SECURE=False
ENV CSRF_COOKIE_SECURE=False
ENV SECURE_SSL_REDIRECT=False

# Окрываем порт
EXPOSE 8000

# Добавляем переменную для порта
ENV PORT=8000

# Команда для запуска сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]