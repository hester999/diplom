from flask import Flask, send_from_directory
from routes import sql_injection_bp  # Изменен путь на относительный
import os
app = Flask(__name__, static_folder='../static', template_folder='../templates')


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:123@localhost:5432/vulnerable_db')

# Сохранение в конфигурации Flask
app.config['DATABASE_URL'] = DATABASE_URL

# Регистрация blueprint с маршрутом для SQL инъекций
app.register_blueprint(sql_injection_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
