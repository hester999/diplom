import time
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_from_directory, session, make_response
import psycopg2
import db

csrf = Blueprint('csrf', __name__, template_folder='../templates', static_folder='../static')

@csrf.route('/csrf/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', message="Пожалуйста, заполните все поля!")

        conn = None
        try:
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT id, password FROM users_csrf WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            cur.close()

            if user:
                user_id, original_password = user
                session['user_id'] = user_id
                session['username'] = username
                session['original_password'] = original_password
                session.modified = True
                return redirect(url_for('csrf.csrf_lvl1'))
            else:
                return render_template('login.html', message="Неверное имя пользователя или пароль!")
        except psycopg2.Error as e:
            return render_template('login.html', message=f"Ошибка базы данных: {str(e)}")
        finally:
            if conn is not None:
                conn.close()

    return render_template('login.html')

@csrf.route('/csrf/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('reg.html', message="Пожалуйста, заполните все поля!")

        conn = None
        try:
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users_csrf WHERE username = %s", (username,))
            if cur.fetchone():
                cur.close()
                return render_template('reg.html', message="Пользователь с таким именем уже существует!")

            cur.execute("INSERT INTO users_csrf (username, password) VALUES (%s, %s) RETURNING id", (username, password))
            result = cur.fetchone()
            if result is None:
                conn.rollback()
                cur.close()
                return render_template('reg.html', message="Ошибка при регистрации: не удалось получить ID пользователя.")
            user_id = result[0]
            conn.commit()
            cur.close()

            session['user_id'] = user_id
            session['username'] = username
            session['original_password'] = password
            session.modified = True

            return render_template('reg.html', message=f"Пользователь {username} успешно зарегистрирован! Теперь вы можете <a href='/csrf/login'>войти</a>.")
        except psycopg2.Error as e:
            return render_template('reg.html', message=f"Ошибка базы данных: {str(e)}")
        finally:
            if conn is not None:
                conn.close()

    return render_template('reg.html')

@csrf.route('/csrf/lvl1', methods=['GET', 'POST'])
def csrf_lvl1():
    if 'user_id' not in session:
        return render_template('lvl1.html', message="Пожалуйста, сначала зарегистрируйтесь и войдите через <a href='/csrf/reg'>регистрацию</a> или <a href='/csrf/login'>вход</a>!")

    username = session['username']
    original_password = session.get('original_password')

    if request.method == 'POST':
        if 'new_password' in request.form:
            new_password = request.form['new_password']
            conn = None
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute("UPDATE users_csrf SET password = %s WHERE id = %s", (new_password, session['user_id']))
                conn.commit()
                cur.close()
            except psycopg2.Error as e:
                return render_template('lvl1.html', message=f"Ошибка базы данных: {str(e)}", username=username)
            finally:
                if conn is not None:
                    conn.close()

        if 'exploit_code' in request.form:
            exploit_code = request.form['exploit_code']
            try:
                new_password = None
                if "new_password=" in exploit_code:
                    start = exploit_code.find("new_password=") + len("new_password=")
                    end = exploit_code.find("&", start) if "&" in exploit_code[start:] else exploit_code.find("'", start)
                    if end == -1:
                        end = len(exploit_code)
                    new_password = exploit_code[start:end].strip("'").strip()

                if new_password:
                    conn = None
                    try:
                        conn = db.get_db()
                        cur = conn.cursor()
                        cur.execute("UPDATE users_csrf SET password = %s WHERE id = %s", (new_password, session['user_id']))
                        conn.commit()
                        cur.close()
                        return render_template('lvl1.html', message="Эксплойт выполнен. Нажмите 'Проверить', чтобы узнать результат.", username=username, show_check=True)
                    finally:
                        if conn is not None:
                            conn.close()
                else:
                    return render_template('lvl1.html', message="Эксплойт не содержит корректного new_password!", username=username)
            except Exception as e:
                return render_template('lvl1.html', message=f"Ошибка выполнения эксплойта: {str(e)}", username=username)

        if 'check' in request.form:
            conn = None
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute("SELECT password FROM users_csrf WHERE id = %s", (session['user_id'],))
                result = cur.fetchone()
                if result is None:
                    return render_template('lvl1.html', message="Пользователь не найден!", username=username, show_check=True)
                current_password = result[0]
                cur.close()

                if current_password == original_password:
                    message = "Эксплойт не удался: Пароль всё ещё тот же."
                    return render_template('lvl1.html', message=message, username=username, show_check=True)
                else:
                    return redirect(url_for('csrf.csrf_lvl2'))
            except psycopg2.Error as e:
                return render_template('lvl1.html', message=f"Ошибка базы данных: {str(e)}", username=username, show_check=True)
            finally:
                if conn is not None:
                    conn.close()

    conn = None
    try:
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users_csrf WHERE username = %s", (username,))
        result = cur.fetchone()
        if result is None:
            return render_template('lvl1.html', message="Пользователь не найден!", username=username)
        user_id = result[0]
        cur.close()
    except psycopg2.Error as e:
        user_id = "Не удалось получить ID"
    finally:
        if conn is not None:
            conn.close()

    return render_template('lvl1.html', username=username, user_id=user_id)

@csrf.route('/csrf/vulnerable', methods=['GET', 'POST'])
def vulnerable():
    if 'user_id' not in session or 'username' not in session:
        return render_template('vulnerable.html', message="Пожалуйста, сначала войдите через <a href='/csrf/login'>вход</a>!")

    username = session['username']

    if 'session_token' not in session:
        session['session_token'] = str(uuid.uuid4())
        session.modified = True

    if request.method == 'POST':
        code = request.form.get('code')
        if code:
            message = "Код выполнен."
            return render_template('vulnerable.html', message=message, code=code, username=username)

    response = make_response(render_template('vulnerable.html', username=username))
    response.set_cookie(
        "csrf_vulnerable_cookie",
        "vulnerable_secret",
        httponly=False,
        samesite="Lax",
        secure=False
    )
    response.set_cookie(
        "session_token",
        session['session_token'],
        httponly=False,
        samesite="Lax",
        secure=False
    )
    return response

@csrf.route('/csrf/lvl2', methods=['GET', 'POST'])
def csrf_lvl2():
    if 'user_id' not in session or 'username' not in session:
        return render_template('lvl2.html', message="Пожалуйста, сначала зарегистрируйтесь и войдите через <a href='/csrf/reg'>регистрацию</a> или <a href='/csrf/login'>вход</a>!")

    if 'session_token' not in session:
        return render_template('lvl2.html', message="Сессионный токен не найден. Пожалуйста, посетите <a href='/csrf/vulnerable'>уязвимую страницу</a> для его создания.")

    username = session['username']

    conn = None
    current_email = "Не удалось получить email"
    try:
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users_csrf WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            current_email = result[0]
        cur.close()
    except psycopg2.Error as e:
        print(f"[ERROR] Ошибка базы данных: {str(e)}")
    finally:
        if conn is not None:
            conn.close()

    if request.method == 'POST':
        if 'new_email' in request.form:
            new_email = request.form['new_email']
            received_session_token = request.args.get('session_token') or request.form.get('session_token')

            if not received_session_token or received_session_token != session['session_token']:
                return render_template('lvl2.html', message="Неверный сессионный токен!", username=username, current_email=current_email)

            conn = None
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute("UPDATE users_csrf SET email = %s WHERE id = %s", (new_email, session['user_id']))
                conn.commit()
                cur.close()
                cur = conn.cursor()
                cur.execute("SELECT email FROM users_csrf WHERE id = %s", (session['user_id'],))
                result = cur.fetchone()
                if result is None:
                    return render_template('lvl2.html', message="Пользователь не найден!", username=username, show_check=True)
                current_email = result[0]
                cur.close()
            except psycopg2.Error as e:
                return render_template('lvl2.html', message=f"Ошибка базы данных: {str(e)}", username=username, current_email=current_email)
            finally:
                if conn is not None:
                    conn.close()

            return render_template('lvl2.html', message="Эксплойт выполнен. Нажмите 'Проверить', чтобы узнать результат.", username=username, show_check=True, current_email=current_email)

        if 'check' in request.form:
            conn = None
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute("SELECT email FROM users_csrf WHERE id = %s", (session['user_id'],))
                result = cur.fetchone()
                if result is None:
                    return render_template('lvl2.html', message="Пользователь не найден!", username=username, show_check=True)
                current_email = result[0]
                cur.close()

                if current_email == 'default@example.com':
                    message = "Эксплойт не удался: Email всё ещё тот же."
                    exploit_success = False
                else:
                    message = f"Эксплойт удался: Email изменён на '{current_email}'!"
                    exploit_success = True
                return render_template('lvl2.html', message=message, username=username, show_check=True, current_email=current_email, exploit_success=exploit_success)
            except psycopg2.Error as e:
                return render_template('lvl2.html', message=f"Ошибка базы данных: {str(e)}", username=username, show_check=True, current_email=current_email)
            finally:
                if conn is not None:
                    conn.close()

    return render_template('lvl2.html', username=username, current_email=current_email)