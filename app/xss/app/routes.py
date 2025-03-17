from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory, session, make_response
# from requests import session
import db
import utils

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


@xss.route('/xss/lvl2', methods=['GET', 'POST'])
def lvl2():
    if request.method == 'POST':
        if 'username' in request.form and 'comment' in request.form:
            username = request.form.get('username', '')
            comment = request.form.get('comment', '')
            if username and comment:
                try:
                    conn = db.get_db()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO xss_comments (username, comment) VALUES (%s, %s)", (username, comment))
                    conn.commit()
                    cur.close()
                    conn.close()
                    return redirect(url_for('lvl2'))
                except Exception as e:
                    return jsonify({"error": f"Ошибка базы данных: {str(e)}"}), 500
        elif 'cookie-input' in request.form:
            cookie = request.form.get('cookie-input', '')
            if cookie == "storage_xss=ce9LADs2aV":
                return redirect(url_for('lvl3'))  # Переход на уровень 3
            else:
                return render_template('lvl2.html', comments=get_comments(), error="Неверные куки. Попробуйте снова.")

    comments = get_comments()
    response = make_response(render_template('lvl2.html', comments=comments))
    # response.set_cookie("xss_vulnerable", "hacked_cookie", httponly=False, samesite="Lax", path="/", secure=False)
    return response


def get_comments():
    try:
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT username, comment, created_at FROM xss_comments ORDER BY created_at DESC;")
        comments = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка чтения комментариев: {str(e)}")
        comments = []
    return comments


@xss.route('/xss/lvl2/user', methods=['GET', 'POST'])
def lvl2_user():
    comments = []
    search_query = None

    if request.method == 'POST':
        search_query = request.form.get('search-username', '')
        if search_query:
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute(
                    "SELECT username, comment, created_at FROM xss_comments WHERE username = %s ORDER BY created_at DESC;",
                    (search_query,))
                comments = cur.fetchall()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Ошибка поиска комментариев: {str(e)}")
                comments = []

    response = make_response(render_template('lvl2_user.html', comments=comments, search_query=search_query))
    response.set_cookie("storage_xss", "ce9LADs2aV", httponly=False, samesite="Lax", secure=False)
    return response


@xss.route('/xss/lvl3', methods=['GET'])
def lvl3():
    return render_template('lvl3.html')


@xss.route('/xss/user', methods=['POST'])
def user():
    payload = request.form.get('payload', '')
    if not payload:
        return render_template('lvl3.html', error="Пейлоад не может быть пустым.")
    link_id = utils.save_xss_link(payload)
    if not link_id:
        return render_template('lvl3.html', error="Ошибка при сохранении пейлоада.")
    return redirect(url_for('xss.lvl3_form', id=link_id))


@xss.route('/xss/lvl3-form', methods=['GET', 'POST'])
def lvl3_form():
    link_id = request.args.get('id', '')
    payload = utils.get_xss_payload(link_id) if link_id else ''
    if not payload:
        payload = ''

    # Проверяем, пришли ли мы с /xss/user (первый переход)
    if link_id and request.referrer and 'xss/user' in request.referrer:
        link = f"http://localhost:8080/xss/lvl3-form?id={link_id}"
        return render_template('lvl3_form.html', username=payload, link=link, show_link=True)

    # Если это POST-запрос (проверка доступа)
    if request.method == 'POST':
        if 'username-input' in request.form and 'password-input' in request.form:
            username_input = request.form.get('username-input', '')
            password_input = request.form.get('password-input', '')
            if username_input == "user123" and password_input == "pass456":
                return redirect('http://localhost:8080/')
            else:
                return render_template('lvl3_form.html', username=payload, error="Неверные данные.")

    # Если это GET-запрос с id (переход по ссылке), показываем форму
    if link_id:
        return render_template('lvl3_form.html', username=payload, show_link=False)

    # Если нет id, показываем форму по умолчанию
    return render_template('lvl3_form.html', username=payload, show_link=False)