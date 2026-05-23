from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
from utils import log_action
import sqlite3

bp = Blueprint('projects', __name__)

@bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, status, created_at FROM projects WHERE owner_id=? ORDER BY created_at DESC", 
            (user_id,)
        )
        # row_factory te deixa fazer isso. Front recebe [{id: 1, name: "Site", ...}]
        projects = [dict(row) for row in cursor.fetchall()]
        return jsonify(projects), 200
    except Exception as e:
        print(f"Erro ao listar projetos: {e}")
        return jsonify({"error": "Erro interno"}), 500
    finally:
        if conn:
            conn.close() # Sempre fecha conexão

@bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validação forte
    if not data or not data.get("name"):
        return jsonify({"error": "Campo 'name' é obrigatório"}), 400
    
    name = data['name'].strip()
    if len(name) < 3 or len(name) > 100:
        return jsonify({"error": "Nome deve ter entre 3 e 100 caracteres"}), 400

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        # Usa 'Planejado' que é um dos valores do CHECK
        cursor.execute(
            "INSERT INTO projects (name, status, owner_id) VALUES (?,?,?)",
            (name, "Planejado", user_id)
        )
        conn.commit()
        
        project_id = cursor.lastrowid
        
        # Busca o projeto recém criado pra retornar pro front
        cursor.execute("SELECT id, name, status, created_at FROM projects WHERE id=?", (project_id,))
        new_project = dict(cursor.fetchone())
        
        log_action(user_id, f"Projeto criado: {name}")
        return jsonify(new_project), 201 # 6. 201 Created + objeto
        
    except sqlite3.Error as e:
        print(f"Erro no banco ao criar projeto: {e}")
        return jsonify({"error": "Erro ao criar projeto"}), 500
    finally:
        if conn:
            conn.close()