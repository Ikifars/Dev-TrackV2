from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
from utils import log_action
import sqlite3

bp = Blueprint('tasks', __name__)

def check_project_owner(cursor, project_id, user_id):
    """Função auxiliar: retorna True se o user é dono do projeto"""
    cursor.execute("SELECT owner_id FROM projects WHERE id=?", (project_id,))
    project = cursor.fetchone()
    if not project:
        return None, jsonify({"error": "Projeto não encontrado"}), 404
    if project['owner_id'] != user_id:
        return None, jsonify({"error": "Acesso negado ao projeto"}), 403
    return project, None, None

@bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get("title") or not data.get("project_id"):
        return jsonify({"error": "Campos obrigatórios: title, project_id"}), 400
    
    title = data['title'].strip()
    if len(title) < 3 or len(title) > 200:
        return jsonify({"error": "Título deve ter entre 3 e 200 caracteres"}), 400
    
    project_id = data['project_id']
    assigned_to = data.get('assigned_to') # Pode ser None
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # AUTORIZAÇÃO: Só dono do projeto pode criar task
        _, error_response, status = check_project_owner(cursor, project_id, user_id)
        if error_response:
            return error_response, status
        
        # Se assigned_to foi passado, valida se o usuário existe
        if assigned_to:
            cursor.execute("SELECT id FROM users WHERE id=?", (assigned_to,))
            if not cursor.fetchone():
                return jsonify({"error": "Usuário atribuído não existe"}), 400
        
        # Usa 'A Fazer' que é o valor do CHECK no banco
        cursor.execute(
            "INSERT INTO tasks (title, status, assigned_to, project_id) VALUES (?,?,?,?)",
            (title, "A Fazer", assigned_to, project_id)
        )
        conn.commit()
        
        task_id = cursor.lastrowid
        cursor.execute("SELECT id, title, status, assigned_to, project_id FROM tasks WHERE id=?", (task_id,))
        new_task = dict(cursor.fetchone())
        
        log_action(user_id, f"Tarefa criada no projeto {project_id}: {title}")
        return jsonify(new_task), 201
        
    except sqlite3.Error as e:
        print(f"Erro no banco ao criar task: {e}")
        return jsonify({"error": "Erro ao criar tarefa"}), 500
    finally:
        if conn:
            conn.close()

@bp.route('/tasks/project/<int:project_id>', methods=['GET'])
@jwt_required()
def list_tasks(project_id):
    user_id = int(get_jwt_identity())
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # AUTORIZAÇÃO: Só dono do projeto lista as tasks
        _, error_response, status = check_project_owner(cursor, project_id, user_id)
        if error_response:
            return error_response, status
            
        cursor.execute(
            "SELECT id, title, status, assigned_to, created_at FROM tasks WHERE project_id=? ORDER BY created_at DESC", 
            (project_id,)
        )
        tasks = [dict(row) for row in cursor.fetchall()]
        return jsonify(tasks), 200
        
    except Exception as e:
        print(f"Erro ao listar tasks: {e}")
        return jsonify({"error": "Erro interno"}), 500
    finally:
        if conn:
            conn.close()

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Busca a task e o dono do projeto dela
        cursor.execute("""
            SELECT t.id, p.owner_id 
            FROM tasks t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id=?
        """, (task_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Tarefa não encontrada"}), 404
            
        if result['owner_id'] != user_id:
            return jsonify({"error": "Apenas o dono do projeto pode deletar tarefas"}), 403
            
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        
        log_action(user_id, f"Tarefa deletada: ID {task_id}")
        return jsonify({"msg": "Tarefa deletada"}), 200
        
    except Exception as e:
        print(f"Erro ao deletar task: {e}")
        return jsonify({"error": "Erro interno"}), 500
    finally:
        if conn:
            conn.close()

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    new_status = data.get('status')
    if new_status not in ['A Fazer', 'Fazendo', 'Feito']:
        return jsonify({"error": "Status inválido"}), 400
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # AUTORIZAÇÃO: Só dono do projeto ou assigned_to pode mudar status
        cursor.execute("""
            SELECT t.assigned_to, p.owner_id 
            FROM tasks t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id=?
        """, (task_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Tarefa não encontrada"}), 404
            
        # Dono do projeto OU pessoa atribuída pode mudar
        if result['owner_id'] != user_id and result['assigned_to'] != user_id:
            return jsonify({"error": "Acesso negado"}), 403
            
        cursor.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
        conn.commit()
        
        cursor.execute("SELECT id, title, status, assigned_to, project_id FROM tasks WHERE id=?", (task_id,))
        updated_task = dict(cursor.fetchone())
        
        log_action(user_id, f"Task {task_id} movida para {new_status}")
        return jsonify(updated_task), 200
        
    except Exception as e:
        print(f"Erro ao atualizar task: {e}")
        return jsonify({"error": "Erro interno"}), 500
    finally:
        if conn:
            conn.close()