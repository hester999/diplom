from flask import Blueprint, request, render_template, current_app
import psycopg2
import textwrap
import os

fix_sql_bp = Blueprint(
    'fix_sql_injection',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

DEFAULT_CODE = textwrap.dedent("""
    def check_login(username, password, cursor):
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        return cursor.fetchone() is not None
""")

code_patch = DEFAULT_CODE


@fix_sql_bp.route("/sql/", methods=["GET"])
def start():
    return render_template("fix_sql_injection_lvl1.html", code=code_patch)


@fix_sql_bp.route("/sql/patch", methods=["POST"])
def patch_code():
    global code_patch
    code_patch = request.form.get("code", DEFAULT_CODE)
    return render_template("fix_sql_injection_lvl1.html", code=code_patch, message="Код обновлён")


@fix_sql_bp.route("/sql/test", methods=["POST"])
def test_login():
    username = request.form["username"]
    password = request.form["password"]

    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()
        local_vars = {}
        exec(code_patch, {}, local_vars)
        result = local_vars['check_login'](username, password, cur)
        cur.close()
        conn.close()
    except Exception as e:
        return render_template("fix_sql_injection_lvl1.html", code=code_patch, message=f"Ошибка: {str(e)}")

    msg = "✅ Авторизация успешна" if result else "❌ Неверные данные"
    return render_template("fix_sql_injection_lvl1.html", code=code_patch, message=msg)


@fix_sql_bp.route("/sql/autotest", methods=["POST"])
def autotest():
    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()
        local_vars = {}
        exec(code_patch, {}, local_vars)
        result = local_vars['check_login']("' OR 1=1 --", "123", cur)
        cur.close()
        conn.close()
    except Exception as e:
        return render_template("fix_sql_injection_lvl1.html", code=code_patch, message=f"Ошибка автотеста: {str(e)}")

    msg = "❌ Уязвимость найдена (SQL-инъекция прошла)" if result else "✅ Уязвимость устранена (инъекция не сработала)"
    return render_template("fix_sql_injection_lvl1.html", code=code_patch, message=msg)
