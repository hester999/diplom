from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.SQL.app.db import get_db
import psycopg2

sql_injection_bp = Blueprint('sql_injection', __name__, template_folder='../templates', static_folder='../static')



# Уровень 1
@sql_injection_bp.route('/sql-injection/lvl1', methods=['GET', 'POST'])
def lvl1():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')

        # Уязвимый запрос с конкатенацией
        if username and password:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            return handle_query(query)
        else:
            return jsonify({"error": "Login and password are required"}), 400

    return render_template('lvl1.html')

@sql_injection_bp.route('/sql-injection/lvl1/answer', methods=['POST'])
def lvl1_answer():
    # Получаем данные из запроса в формате JSON
    data = request.get_json()

    # Извлекаем логин и пароль
    admin_login = data.get('admin_login')
    admin_password = data.get('admin_password')

    # Правильные логин и пароль администратора
    if admin_login == 'main_admin' and admin_password == 'mainadminpassword':
        return jsonify({"message": "Авторизация успешна"}), 200  # Ответ 200 OK
    else:
        return jsonify({"error": "Invalid login or password"}), 403  # Ответ 403 Forbidden

# Уровень 2
@sql_injection_bp.route('/sql-injection/lvl2', methods=['GET', 'POST'])
def lvl2():
    if request.method == 'POST':
        query = request.form.get('query')
        return handle_query(query)
    return render_template('lvl2.html')

# Общая функция для выполнения запросов
def handle_query(query):
    """Обрабатываем SQL-запрос от пользователя с конкатенацией"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Логируем SQL-запрос перед выполнением
        print(f"Executing query: {query}")

        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            return jsonify({"result": result}), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except psycopg2.Error as e:
        print(f"SQL error: {str(e)}")
        return jsonify({"error": f"SQL error: {str(e)}"}), 400
