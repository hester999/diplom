from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.SQL.app.db import get_db
import handlers.handler_lvl1
import handlers.handler_lvl2
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
            return handlers.handler_lvl1.handle_query(query)
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


@sql_injection_bp.route('/sql-injection/lvl2', methods=['POST', 'GET'])
def lvl2():
    if request.method == 'POST':
        # Получаем данные из формы
        data = request.get_json()
        username = data.get('login')
        password = data.get('password')

        if username and password:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            return handlers.handler_lvl2.handle_query_lvl2(query)
        else:
            return jsonify({"error": "Login and password are required"}), 400
    return render_template('lvl2.html')

@sql_injection_bp.route('/sql-injection/lvl2/answer', methods=['POST'])
def lvl2_answer():
    try:
        data = request.get_json()
        student_answer = data.get('student_answer')

        print(student_answer)

        # Заменяем запятую на точку
        student_answer = student_answer.replace(',', '.')

        con = get_db()
        cur = con.cursor()
        cur.execute("""
        SELECT min(u.price) FROM
        (SELECT * FROM users
        INNER JOIN orders ON orders.user_id = users.id
        INNER JOIN products ON orders.product_id = products.id
        WHERE users.username = 'main_admin'
        LIMIT 3) as u
        """)
        min_price = cur.fetchone()[0]

        if min_price is None:
            return jsonify({"error": "No data found for the minimum price."}), 404

        if  student_answer == str(min_price):
            return jsonify({"message": "Correct! Proceeding to next level."}), 200
        else:
            return jsonify({"error": "Incorrect answer. Please try again."}), 403
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request."}), 500