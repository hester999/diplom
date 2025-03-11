import os

from flask import Flask
from routes import attacker

app = Flask(__name__, static_folder='../static', template_folder='../templates')



DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:123@localhost:5432/vulnerable_db')

app.config['DATABASE_URL'] = DATABASE_URL
# Регистрируем blueprint атакера
app.register_blueprint(attacker)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
