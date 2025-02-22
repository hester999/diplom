from flask import jsonify

# from app.SQL.app.db import get_db
from db import get_db


def handle_query_lvl4(query):
    """Обрабатывает SQL-запрос, позволяя выполнить инъекцию"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Логируем SQL-запрос
        print(f"Executing query: {query}")

        cursor.execute(query)
        conn.commit()
        cursor.execute("select count(username) from users where username = 'hacker';")
        result = cursor.fetchone()[0]


        if result > 0:
            return jsonify({"result": 200}), 200
        else:
            return jsonify({"error": "No data found"}), 404


    except Exception as e:
        print(f"SQL error: {str(e)}")
        return jsonify({"error": f"SQL error: {str(e)}"}), 400
