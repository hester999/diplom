import time
from flask import Blueprint, render_template, request, session, redirect, url_for
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
                session['original_password'] = original_password  # Сохраняем исходный пароль в сессии
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
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()

            session['user_id'] = user_id
            session['username'] = username
            session['original_password'] = password  # Сохраняем исходный пароль в сессии
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
    original_password = session.get('original_password')  # Получаем исходный пароль из сессии

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
                current_password = cur.fetchone()[0]
                cur.close()

                if current_password == original_password:
                    message = "Эксплойт не удался: Пароль всё ещё тот же."
                    return render_template('lvl1.html', message=message, username=username, show_check=True)
                else:
                    # Если эксплойт успешен, перенаправляем на lvl2
                    return redirect(url_for('csrf.csrf_lvl2'))

            except psycopg2.Error as e:
                return render_template('lvl1.html', message=f"Ошибка базы данных: {str(e)}", username=username, show_check=True)
            finally:
                if conn is not None:
                    conn.close()

    # Получаем ID пользователя для отображения
    conn = None
    try:
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users_csrf WHERE username = %s", (username,))
        user_id = cur.fetchone()[0]
        cur.close()
    except psycopg2.Error as e:
        user_id = "Не удалось получить ID"
    finally:
        if conn is not None:
            conn.close()

    return render_template('lvl1.html', username=username, user_id=user_id)

@csrf.route('/csrf/lvl2', methods=['GET'])
def csrf_lvl2():
    if 'user_id' not in session:
        return render_template('lvl2.html', message="Пожалуйста, сначала пройдите Уровень 1 через <a href='/csrf/lvl1'>Уровень 1</a>!")

    username = session['username']
    return render_template('lvl2.html', username=username, message="Поздравляем! Вы успешно прошли Уровень 1. Это пока конец задания, но вы можете попробовать снова с другим пользователем.")