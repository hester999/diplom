import time
from flask import Blueprint, render_template, request, session
import psycopg2  # Добавляем импорт psycopg2
import db  # Предполагается, что db.get_db() возвращает соединение

csrf = Blueprint('csrf', __name__, template_folder='../templates', static_folder='../static')

@csrf.route('/csrf/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('reg.html', message="Пожалуйста, заполните все поля!")

        try:
            conn = db.get_db()
            cur = conn.cursor()
            # Проверяем, существует ли пользователь
            cur.execute("SELECT id FROM users_csrf WHERE username = %s", (username,))
            if cur.fetchone():
                cur.close()
                conn.close()
                return render_template('reg.html', message="Пользователь с таким именем уже существует!")

            # Создаём нового пользователя
            cur.execute("INSERT INTO users_csrf (username, password) VALUES (%s, %s) RETURNING id", (username, password))
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            # Сохраняем данные в сессии
            session['user_id'] = user_id
            session['username'] = username
            session['original_password'] = password
            session.modified = True  # Убеждаемся, что сессия сохранена

            return render_template('reg.html', message=f"Пользователь {username} успешно зарегистрирован! Теперь перейдите на <a href='/csrf/lvl1'>Уровень 1</a> для выполнения задания.")

        except psycopg2.Error as e:
            return render_template('reg.html', message=f"Ошибка базы данных: {str(e)}")

    return render_template('reg.html')

@csrf.route('/csrf/lvl1', methods=['GET', 'POST'])
def csrf_lvl1():
    if 'user_id' not in session:
        return render_template('lvl1.html', message="Пожалуйста, сначала зарегистрируйтесь через <a href='/csrf/reg'>регистрацию</a>!")

    username = session['username']
    original_password = session['original_password']

    if request.method == 'POST':
        # Уязвимый эндпоинт для смены пароля (например, от формы или эксплойта)
        if 'new_password' in request.form:
            new_password = request.form['new_password']
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute("UPDATE users_csrf SET password = %s WHERE id = %s", (new_password, session['user_id']))
                conn.commit()
                cur.close()
                conn.close()
            except psycopg2.Error as e:
                return render_template('lvl1.html', message=f"Ошибка базы данных: {str(e)}", username=username)

        # Выполнение эксплойта
        if 'exploit_code' in request.form:
            exploit_code = request.form['exploit_code']
            try:
                # Эмулируем выполнение эксплойта, извлекая new_password из кода
                new_password = None
                if "new_password=" in exploit_code:
                    start = exploit_code.find("new_password=") + len("new_password=")
                    end = exploit_code.find("&", start) if "&" in exploit_code[start:] else exploit_code.find("'", start)
                    if end == -1:
                        end = len(exploit_code)
                    new_password = exploit_code[start:end].strip("'").strip()

                if new_password:
                    conn = db.get_db()
                    cur = conn.cursor()
                    cur.execute("UPDATE users_csrf SET password = %s WHERE id = %s", (new_password, session['user_id']))
                    conn.commit()
                    cur.close()
                    conn.close()
                    return render_template('lvl1.html', message="Эксплойт выполнен. Нажмите 'Проверить', чтобы узнать результат.", username=username, show_check=True)
                else:
                    return render_template('lvl1.html', message="Эксплойт не содержит корректного new_password!", username=username)
            except Exception as e:
                return render_template('lvl1.html', message=f"Ошибка выполнения эксплойта: {str(e)}", username=username)

        # Проверка результата
        if 'check' in request.form:
            try:
                conn = db.get_db()
                cur = conn.cursor()
                cur.execute("SELECT password FROM users_csrf WHERE id = %s", (session['user_id'],))
                current_password = cur.fetchone()[0]
                cur.close()
                conn.close()

                if current_password == original_password:
                    message = "Эксплойт не удался: Пароль всё ещё тот же."
                else:
                    message = f"Эксплойт удался: Пароль изменён на '{current_password}'!"
                return render_template('lvl1.html', message=message, username=username, show_check=True)
            except psycopg2.Error as e:
                return render_template('lvl1.html', message=f"Ошибка базы данных: {str(e)}", username=username, show_check=True)

    return render_template('lvl1.html', username=username)