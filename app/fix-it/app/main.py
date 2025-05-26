from flask import Flask
from routes_sql import fix_sql_bp
from routes_csrf import fix_csrf_bp
from routes_xss import fix_xss_bp
import os

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://admin:123@localhost:5432/vulnerable_db')
app.secret_key = "supersecretkey"
# Регистрация всех модулей
app.register_blueprint(fix_sql_bp)
app.register_blueprint(fix_csrf_bp)
app.register_blueprint(fix_xss_bp)
# app.register_blueprint(fix_file_upload_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
