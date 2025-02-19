from flask import Flask
from app.SQL.app.routes import sql_injection_bp  # Изменен путь на относительный

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Конфигурация приложения
app.config['DATABASE'] = 'vulnerable_db'
app.config['USER'] = 'admin'
app.config['PASSWORD'] = '123'
app.config['HOST'] = 'localhost'
app.config['PORT'] = '5432'

# Регистрация blueprint с маршрутом для SQL инъекций
app.register_blueprint(sql_injection_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
