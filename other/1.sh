#!/bin/bash

## Путь к корневой папке проекта
#PROJECT_DIR="application"
#
## Создание корневой папки проекта
#mkdir -p $PROJECT_DIR
#cd $PROJECT_DIR

# Создание виртуального окружения (если его нет)
# python3 -m venv venv
# Считаем, что виртуальное окружение уже создано

# Создание основной структуры
mkdir -p app/sql-injection
mkdir -p app/xss
mkdir -p app/csrf
mkdir -p app/file-upload

# Создание папок для статики
mkdir -p app/sql-injection/static/CSS
mkdir -p app/sql-injection/static/JS
mkdir -p app/xss/static/CSS
mkdir -p app/xss/static/JS
mkdir -p app/csrf/static/CSS
mkdir -p app/csrf/static/JS
mkdir -p app/file-upload/static/CSS
mkdir -p app/file-upload/static/JS

# Создание папок для шаблонов
mkdir -p app/sql-injection/templates
mkdir -p app/xss/templates
mkdir -p app/csrf/templates
mkdir -p app/file-upload/templates

# Создание папок для файлов в приложении
mkdir -p app/sql-injection/app
mkdir -p app/xss/app
mkdir -p app/csrf/app
mkdir -p app/file-upload/app

# Создание Dockerfile для каждого сервиса
cat > docker-compose.yml <<EOL
version: '3'
services:
  sql_injection:
    build: ./app/sql-injection
    ports:
      - "5001:5001"
    volumes:
      - .:/app
    environment:
      - FLASK_APP=app.sql_injection.app.main
      - FLASK_ENV=development
  xss:
    build: ./app/xss
    ports:
      - "5002:5002"
    volumes:
      - .:/app
    environment:
      - FLASK_APP=app.xss.app.main
      - FLASK_ENV=development
  csrf:
    build: ./app/csrf
    ports:
      - "5003:5003"
    volumes:
      - .:/app
    environment:
      - FLASK_APP=app.csrf.app.main
      - FLASK_ENV=development
  file_upload:
    build: ./app/file-upload
    ports:
      - "5004:5004"
    volumes:
      - .:/app
    environment:
      - FLASK_APP=app.file_upload.app.main
      - FLASK_ENV=development
EOL

# Создание Dockerfile для SQL инъекций (для всех сервисов будет схожий)
cat > app/sql-injection/Dockerfile <<EOL
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
EOL

# Создание requirements.txt
touch requirements.txt

# Пример requirements.txt
cat > requirements.txt <<EOL
Flask
psycopg2
flask-cors
EOL

# Создание основного файла приложения для SQL инъекций (app/SQL/app/main.py)
cat > app/sql-injection/app/main.py <<EOL
from flask import Flask
from app.sql_injection.app.routes import sql_injection_bp

app = Flask(__name__)

# Конфигурация приложения
app.config['DATABASE'] = 'vulnerable_db'
app.config['USER'] = 'admin'
app.config['PASSWORD'] = '123'
app.config['HOST'] = 'localhost'
app.config['PORT'] = '5432'

# Регистрация blueprint с маршрутом для SQL инъекций
app.register_blueprint(sql_injection_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
EOL

# Пример создания обработчиков для SQL инъекций (routes.py)
cat > app/sql-injection/app/routes.py <<EOL
from flask import Blueprint, render_template, request, jsonify
from app.sql_injection.app.db import get_db
import psycopg2

sql_injection_bp = Blueprint('sql_injection', __name__)

# Уровень 1
@sql_injection_bp.route('/sql-injection/lvl1', methods=['GET', 'POST'])
def lvl1():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        query = f"SELECT * FROM users WHERE username='{login}' AND password='{password}'"
        return handle_query(query)
    return render_template('lvl1.html')

# Общая функция для обработки запроса
def handle_query(query):
    """Обрабатываем SQL-запрос от пользователя"""
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            return jsonify({"result": result}), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except psycopg2.Error as e:
        return jsonify({"error": f"SQL error: {str(e)}"}), 400
EOL

# Создание подключения к базе данных в db.py
cat > app/sql-injection/app/db.py <<EOL
import psycopg2
from flask import current_app

def get_db():
    """Подключение к базе данных PostgreSQL"""
    conn = psycopg2.connect(
        dbname=current_app.config['DATABASE'],
        user=current_app.config['USER'],
        password=current_app.config['PASSWORD'],
        host=current_app.config['HOST'],
        port=current_app.config['PORT']
    )
    return conn
EOL

# Создание шаблона для первого уровня инъекций (lvl1.html)
cat > app/sql-injection/templates/lvl1.html <<EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Injection Level 1</title>
</head>
<body>
    <header>
        <h1>SQL Injection Level 1</h1>
    </header>

    <section>
        <h2>Задание:</h2>
        <p>Попробуйте выполнить запрос с простой SQL инъекцией для обхода пароля.</p>

        <form method="POST">
            <label for="login">Логин:</label>
            <input type="text" id="login" name="login"><br><br>

            <label for="password">Пароль:</label>
            <input type="text" id="password" name="password"><br><br>

            <button type="submit">Отправить запрос</button>
        </form>

        <div id="result"></div>
    </section>
</body>
</html>
EOL

echo "Структура проекта создана!"
