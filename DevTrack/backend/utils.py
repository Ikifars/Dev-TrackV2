from database import get_db
import sqlite3

def log_action(user_id, action):
    """
    Registra ação do usuário. Falha silenciosamente para não quebrar
    o fluxo principal se o log der erro.
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (action, user_id) VALUES (?,?)", 
            (action, user_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        # 1. Log não pode quebrar a aplicação principal
        # Se der erro no log, só printa e continua
        print(f"Erro ao registrar log: {e}")
    finally:
        # 2. SEMPRE fecha a conexão
        if conn:
            conn.close()