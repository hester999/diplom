import psycopg2
from flask import jsonify

from db import get_db


def handle_query_lvl2(query):
    """Обрабатываем SQL-инъекцию и возвращаем список таблиц, если она успешна"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if result:  # Если запрос выполнен успешно
            # Предполагаем, что результат — это список таблиц
            cleaned_result = [row[0] for row in result if row[0] is not None]
            return cleaned_result  # Возвращаем список таблиц
        else:
            return jsonify({"error": "No matching users found."}), 404

    except Exception as e:
        print(f"SQL error: {str(e)}")
        return jsonify({"error": f"SQL error: {str(e)}"}), 400