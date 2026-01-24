from flask_cors import CORS
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from database import get_db
from utils import log_action
import bcrypt

bp = Blueprint('auth', __name__)
CORS(bp)

@bp.route('/register', methods=['POST','OPTIONS'])
def register():
    data = request.json
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Campos obrigatórios"}), 400

    hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (data.get('name', ''), data['email'], hashed)
        )
        conn.commit()
        log_action(cursor.lastrowid, "Usuário registrado")
        return jsonify({"msg": "Usuário criado"})
    except:
        return jsonify({"error": "Email já cadastrado"}), 400

@bp.route('/login', methods=['OPTIONS'])
def login_options():
    return '', 204

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM users WHERE email=?", (data.get('email'),))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(data.get('password', '').encode(), user[1]):
        token = create_access_token(identity=user[0], expires_delta=timedelta(hours=2))
        log_action(user[0], "Login realizado")
        return jsonify({"token": token})

    return jsonify({"error": "Credenciais inválidas"}), 401
