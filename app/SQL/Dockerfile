# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем приложение в контейнер
COPY . /app

# Открываем порт 5001 для SQL инъекций
EXPOSE 5001

# Запускаем Flask приложение
CMD ["python", "app/sql-injection/app/main.py"]
