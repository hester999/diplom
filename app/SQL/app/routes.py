from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory
from db import get_db
import handlers.handler_lvl1
import handlers.handler_lvl2
import handlers.handler_lvl3
import handlers.handler_lvl4
import psycopg2

sql_injection_bp = Blueprint('sql_injection', __name__, template_folder='../templates', static_folder='/static')


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




@sql_injection_bp.route('/sql-injection/lvl2', methods=['POST',"GET"])
def lvl2():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('login')
        password = data.get('password')

        if username and password:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            result = handlers.handler_lvl2.handle_query_lvl2(query)

            if result:
                # Получаем список таблиц из базы данных
                con = get_db()
                cur = con.cursor()
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = [row[0] for row in cur.fetchall()]

                return jsonify({
                    "result": tables  # Отправляем список таблиц
                }), 200
            else:
                return jsonify({"error": "No result found."}), 404
    return render_template('lvl2.html')


@sql_injection_bp.route('/sql-injection/lvl2/answer', methods=['POST'])
def lvl2_answer():
    student_answer = request.get_json('student_answer')
    print(type(student_answer))
    s = student_answer.get('student_answer')


    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cur.fetchall()]
    print(tables)

    # Проверяем ответ пользователя
    correct_answer = ", ".join(tables)  # Список таблиц через запятую
    if s == correct_answer:
        return jsonify({"message": "Correct! Proceeding to next level."}), 200
    else:
        return jsonify({"error": "Incorrect answer. Please try again."}), 403


@sql_injection_bp.route('/sql-injection/lvl3', methods=['POST', 'GET'])
def lvl3():
    if request.method == 'POST':
        # Получаем данные из формы
        data = request.get_json()
        username = data.get('login')
        password = data.get('password')

        if username and password:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            return handlers.handler_lvl3.handle_query_lvl3(query)
        else:
            return jsonify({"error": "Login and password are required"}), 400
    return render_template('lvl3.html')


@sql_injection_bp.route('/sql-injection/lvl3/answer', methods=['POST'])
def lvl3_answer():
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

        if student_answer == str(min_price):
            return jsonify({"message": "Correct! Proceeding to next level."}), 200
        else:
            return jsonify({"error": "Incorrect answer. Please try again."}), 403
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request."}), 500



@sql_injection_bp.route('/sql-injection/lvl4', methods=['POST', 'GET'])
def lvl4():
    if request.method == 'POST':
        # Получаем данные из формы
        data = request.get_json()
        username = data.get('login')
        password = data.get('password')

        if username and password:
            # Уязвимый запрос с возможностью SQL-инъекции
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            return handlers.handler_lvl4.handle_query_lvl4(query)
        else:
            return jsonify({"error": "Login and password are required"}), 400

    return render_template('lvl4.html')

@sql_injection_bp.route('/sql-injection/lvl4/answer', methods=['POST'])
def lvl4_answer():
    try:
        flag  = False
        con = get_db()
        cur = con.cursor()

        # Проверяем, существует ли запись с user_id = -1 и secret_info = 'sql-injection'
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'hacker'")
        count = cur.fetchone()[0]
        print(count)

        if count > 0:
            flag = True
            cur.execute("delete from users where username = 'hacker';")
            con.commit()

        if flag:
            return jsonify({"message": "Injection successful! Record deleted. Proceeding to next level."}), 200
        else:
            return jsonify({"error": "Injection not found. Try again."}), 403

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

