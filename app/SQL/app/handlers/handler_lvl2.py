import psycopg2
from flask import jsonify

from app.SQL.app.db import get_db


def handle_query_lvl2(query):
    """Обрабатываем запрос с инъекцией для получения списка таблиц"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            # Форматируем результат для отображения
            table_names = [row[0] for row in result]
            return jsonify({"result": table_names}), 200
        else:
            return jsonify({"error": "No tables found."}), 404

    except Exception as e:
        print(f"SQL error: {str(e)}")
        return jsonify({"error": f"SQL error: {str(e)}"}), 400


