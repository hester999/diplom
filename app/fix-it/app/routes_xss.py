from flask import Blueprint, request, render_template, current_app
import psycopg2
import textwrap
import html

fix_xss_bp = Blueprint(
    'fix_xss',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# Уязвимая функция по умолчанию
DEFAULT_CODE = textwrap.dedent("""
    def sanitize_and_save(name, comment, cursor):
       
        query = "INSERT INTO xss_comments (username, comment) VALUES (%s, %s)"
        cursor.execute(query, (name, comment))
""")

code_patch = DEFAULT_CODE


@fix_xss_bp.route("/xss/", methods=["GET"])
def xss_index():
    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("SELECT username, comment FROM xss_comments ORDER BY id DESC")
        comments = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        comments = []
    return render_template("2.html", code=code_patch, comments=comments)


@fix_xss_bp.route("/xss/patch", methods=["POST"])
def patch_code_xss():
    global code_patch
    code_patch = request.form.get("code", DEFAULT_CODE)
    return xss_index()


@fix_xss_bp.route("/xss/test", methods=["POST"])
def test_comment_xss():
    username = request.form["username"]
    comment = request.form["comment"]

    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()
        local_vars = {}
        exec(code_patch, {}, local_vars)
        local_vars['sanitize_and_save'](username, comment, cur)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return render_template("2.html", code=code_patch, message=f"Ошибка: {str(e)}", comments=[])

    return xss_index()


@fix_xss_bp.route("/xss/autotest", methods=["POST"])
def autotest_xss():
    test_payload = "<script>alert('XSS')</script>"

    try:
        conn = psycopg2.connect(current_app.config["DATABASE_URL"])
        cur = conn.cursor()

        # Очищаем таблицу перед тестом (если нужно)
        cur.execute("DELETE FROM xss_comments")

        # Выполняем пользовательский код
        local_vars = {}
        sandbox = {'html': html}
        exec(code_patch, sandbox, sandbox)
        sandbox['sanitize_and_save']("attacker", test_payload, cur)

        cur.execute("SELECT comment FROM xss_comments ORDER BY id DESC LIMIT 1")
        stored_comment = cur.fetchone()[0]
        cur.close()
        conn.commit()
        conn.close()

        if "<script>" in stored_comment:
            msg = "❌ Уязвимость осталась: скрипт не отфильтрован"
        else:
            msg = "✅ Уязвимость устранена: скрипт очищен"

    except Exception as e:
        msg = f"❌ Ошибка при автотесте: {str(e)}"

    return render_template("2.html", code=code_patch, message=msg, comments=[])
