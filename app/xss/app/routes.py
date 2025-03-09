from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory

xss = Blueprint('xss', __name__, template_folder='../templates', static_folder='../static')




user_payload = ""

@xss.route('/xss/lvl1', methods=['GET', 'POST'])
def lvl1():
    global user_payload
    if request.method == 'POST':
        data = request.get_json()
        payload = data.get('payload', '')

        if "<script>" in payload.lower() and "alert" in payload.lower():
            user_payload = payload  # Сохраняем инъекцию
            return jsonify({"message": "XSS detected!"}), 200
        else:
            return jsonify({"error": "Invalid XSS payload"}), 400

    return render_template('lvl1.html', user_payload=user_payload)
    # Отображаем введенный пользователем payload

@xss.route('/xss/lvl2')
def lvl2():
    return render_template("lvl2.html")