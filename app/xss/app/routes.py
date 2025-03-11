from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory,session,make_response
# from requests import session

xss = Blueprint('xss', __name__, template_folder='../templates', static_folder='../static')

# Устанавливаем секретный ключ для сессии
SECRET_KEY = "supersecretkey"  # Можно изменить на что-то сложное
SESSION_COOKIE_NAME = "xss_session"

@xss.route('/xss/lvl1', methods=['GET', 'POST'])
def lvl1():
    global user_payload
    if request.method == 'POST':
        data = request.get_json()
        payload = data.get('payload', '')
        user_payload = payload
        return jsonify({"message": "Payload received!", "payload": user_payload}), 200

    response = make_response(render_template('lvl1.html'))
    response.set_cookie(
        "xss_vulnerable",
        "hacked_cookie",
        httponly=False,
        samesite="Lax",  # Измените на "Lax" для теста через HTTP
        path="/",  # Доступна для всех путей
        secure=False  # Для HTTP
    )
    return response

@xss.route('/xss/lvl1/payload', methods=['GET'])
def get_xss_payload():
    """Возвращает сохраненный XSS-пейлоад"""
    return jsonify({"payload": user_payload})

@xss.route('/xss/lvl1/log', methods=['POST'])
def log_xss_execution():
    """Логирует успешное выполнение XSS-инъекции"""
    data = request.get_json()
    if data.get("success"):
        print(f"[XSS EXECUTED]: {data.get('payload')}")
        return jsonify({"message": "XSS executed!"}), 200
    return jsonify({"error": "Invalid request"}), 400