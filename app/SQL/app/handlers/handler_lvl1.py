# Функция для выполнения запроса с инъекцией
import psycopg2
from flask import jsonify

from db import get_db

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