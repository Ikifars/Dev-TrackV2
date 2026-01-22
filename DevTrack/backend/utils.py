from database import get_db

def log_action(user_id, action):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (action, user_id) VALUES (?, ?)", (action, user_id))
    conn.commit()
