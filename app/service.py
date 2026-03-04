from app.db import get_connection
from app.retry import retry_decorator
from app.circuit import db_breaker

@db_breaker
@retry_decorator
def insert_user(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, name, email, phone) VALUES (%s,%s,%s,%s)",
        (data["user_id"], data["name"], data["email"], data["phone"])
    )
    conn.commit()
    cur.close()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result
