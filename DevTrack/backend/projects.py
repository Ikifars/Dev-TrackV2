from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
from utils import log_action

bp = Blueprint('projects', __name__)

@bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status FROM projects WHERE owner_id=?", (user_id,))
    return jsonify(cursor.fetchall())

@bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.json

    if not data.get("name"):
        return jsonify({"error": "Nome obrigatório"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, status, owner_id) VALUES (?, ?, ?)",
                   (data['name'], "Ativo", user_id))
    conn.commit()
    log_action(user_id, f"Projeto criado: {data['name']}")
    return jsonify({"msg": "Projeto criado"})
