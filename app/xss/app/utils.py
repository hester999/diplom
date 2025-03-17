# ./app/xss/utils.py
import uuid
import psycopg2
from db import get_db

def generate_unique_id():
    """Генерирует уникальный идентификатор для ссылки."""
    return str(uuid.uuid4())

def save_xss_link(payload):
    """Сохраняет XSS-пейлоад и возвращает уникальный ID ссылки."""
    link_id = generate_unique_id()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO xss_links (link_id, payload) VALUES (%s, %s)", (link_id, payload))
        conn.commit()
        cur.close()
        conn.close()
        return link_id
    except Exception as e:
        print(f"Ошибка записи в БД: {str(e)}")
        return None

def get_xss_payload(link_id):
    """Получает XSS-пейлоад по ID ссылки."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT payload FROM xss_links WHERE link_id = %s", (link_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Ошибка чтения из БД: {str(e)}")
        return None