import psycopg2
from flask import current_app

def get_db():
    """Подключение к базе данных PostgreSQL"""
    conn = psycopg2.connect(
        dbname=current_app.config['DATABASE'],
        user=current_app.config['USER'],
        password=current_app.config['PASSWORD'],
        host=current_app.config['HOST'],
        port=current_app.config['PORT']
    )
    return conn
