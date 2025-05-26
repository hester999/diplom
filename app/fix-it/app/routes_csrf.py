from flask import Blueprint, request, render_template, current_app, session
import psycopg2
import textwrap
import html

fix_csrf_bp = Blueprint(
    'fix_csrf',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

DEFAULT_CODE = textwrap.dedent("""
    # Подсказка: используйте эту функцию для генерации токена
    # def generate_token(session):
    #     from uuid import uuid4
    #     token = str(uuid4())
    #     session['csrf_token'] = token
    #     return token

    def change_password(new_password, token, session_token, cursor):
        # TODO: Добавьте проверку токена здесь
        cursor.execute("UPDATE users SET password = %s WHERE id = 1", (new_password,))
""")

code_patch = DEFAULT_CODE


@fix_csrf_bp.route("/csrf/", methods=["GET"])
def csrf_index():
    return render_template("fix_csrf_lvl1.html", code=code_patch, csrf_token=session.get("csrf_token", "токен не создан"))


@fix_csrf_bp.route("/csrf/patch", methods=["POST"])
def patch_code_csrf():
    global code_patch
    code_patch = request.form.get("code", DEFAULT_CODE)
    return csrf_index()


@fix_csrf_bp.route("/csrf/test", methods=["POST"])
def test_csrf():
    new_password = request.form.get("new_password", "")
    token = request.form.get("csrf_token", "")
    session_token = session.get("csrf_token", "")

    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()

        local = {'session': session}
        exec(code_patch, local, local)
        local['change_password'](new_password, token, session_token, cur)

        conn.commit()
        cur.close()
        conn.close()
        msg = "✅ Пароль изменён"
    except Exception as e:
        msg = f"❌ Ошибка: {str(e)}"

    return render_template("fix_csrf_lvl1.html", code=code_patch, message=msg, csrf_token=session.get("csrf_token", ""))


@fix_csrf_bp.route("/csrf/autotest", methods=["POST"])
def autotest_csrf():
    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()

        success, msg = check(session, cur, code_patch)

        cur.close()
        conn.rollback()
        conn.close()
    except Exception as e:
        msg = f"❌ Ошибка при автотесте: {str(e)}"

    return render_template("fix_csrf_lvl1.html", code=code_patch, message=msg, csrf_token=session.get("csrf_token", ""))


def check(session, cursor, code_patch):
    local = {'session': session}
    exec(code_patch, local, local)

    if 'generate_token' not in local or 'change_password' not in local:
        return False, "❌ Не найдены функции generate_token или change_password"

    token = local['generate_token'](session)

    try:
        local['change_password']("hacked123", token, session, cursor)
    except Exception as e:
        return False, f"❌ Ошибка в change_password: {str(e)}"

    return True, "✅ Уязвимость устранена: токен проверяется"