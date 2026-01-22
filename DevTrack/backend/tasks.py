from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
from utils import log_action

bp = Blueprint('tasks', __name__)

@bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.json

    if not data.get("title") or not data.get("project_id"):
        return jsonify({"error": "Dados incompletos"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, status, assigned_to, project_id) VALUES (?, ?, ?, ?)",
                   (data['title'], "To Do", data.get('assigned_to'), data['project_id']))
    conn.commit()
    log_action(user_id, f"Tarefa criada: {data['title']}")
    return jsonify({"msg": "Tarefa criada"})

@bp.route('/tasks/<int:project_id>', methods=['GET'])
@jwt_required()
def list_tasks(project_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM tasks WHERE project_id=?", (project_id,))
    return jsonify(cursor.fetchall())
