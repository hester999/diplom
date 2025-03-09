from flask import Flask, send_from_directory
from routes import xss
import os
app = Flask(__name__, static_folder='../static', template_folder='../templates')


# Конфигурация приложения
app.config['DATABASE'] = 'vulnerable_db'
app.config['USER'] = 'admin'
app.config['PASSWORD'] = '123'
app.config['HOST'] = 'localhost'
app.config['PORT'] = '5432'

# DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:123@localhost:5432/vulnerable_db')

# Сохранение в конфигурации Flask
# app.config['DATABASE_URL'] = DATABASE_URL
app.register_blueprint(xss)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
