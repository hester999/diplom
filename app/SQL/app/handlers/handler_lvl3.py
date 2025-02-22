from flask import jsonify

from db import get_db


def handle_query_lvl3(query):
    """Обрабатываем запрос с инъекцией"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            # Формируем результат
            formatted_result = [{"username": row[1], "password": row[2], "product_name": row[8], "price": row[9]} for row in result]
            # Возвращаем результат в формате JSON
            return jsonify({"result": formatted_result}), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except Exception as e:
        print(f"SQL error: {str(e)}")
        return jsonify({"error": f"SQL error: {str(e)}"}), 400