# Используем официальный образ Python
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт (если нужно, например, для Flask)
EXPOSE 5000

# Запускаем приложение
CMD ["python", "./app/main.py"]