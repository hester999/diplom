import psycopg2
from flask import current_app

def get_db():
    """Подключение к базе данных PostgreSQL"""

    conn = psycopg2.connect(current_app.config['DATABASE_URL'])

    return conn
