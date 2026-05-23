from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from database import get_db
from utils import log_action
import bcrypt
import sqlite3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address) # Usa o IP pra limitar

@bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute") # Rate limit: evita spam de contas
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Campos obrigatórios: email, password"}), 400

    # Validação mínima de senha
    if len(data['password']) < 8:
        return jsonify({"error": "Senha deve ter no mínimo 8 caracteres"}), 400

    # Bcrypt + decode pra string
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?,?,?)",
            (data.get('name', ''), data['email'], hashed)
        )
        conn.commit()
        user_id = cursor.lastrowid
        log_action(user_id, "Usuário registrado")
        return jsonify({"msg": "Usuário criado"}), 201 # 201 = Created

    except sqlite3.IntegrityError: # Erro específico pra email duplicado
        return jsonify({"error": "Email já cadastrado"}), 409 # 409 = Conflict
    except Exception as e:
        # Loga o erro real mas não vaza pro usuário
        print(f"Erro no registro: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close() # Sempre fecha conexão

@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  Rate limit anti brute-force
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Campos obrigatórios"}), 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=?", (data.get('email'),))
        user = cursor.fetchone()

        # Compara com encode e precisa do decode que fizemos no register
        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user[1].encode('utf-8')):
            # 9. Remove expires_delta: usa o padrão do app.py de 15min
            token = create_access_token(identity=str(user[0]))
            log_action(user[0], "Login realizado")
            return jsonify({"token": token, "expires_in": 900}), 200

        #  Resposta genérica pra não dar dica se email existe ou não
        return jsonify({"error": "Credenciais inválidas"}), 401

    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500
    finally:
        if conn:
            conn.close()