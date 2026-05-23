import sqlite3

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Permite acessar como dict: user['email']
    conn.execute("PRAGMA foreign_keys = ON") # Ativa Foreign Keys
    conn.execute("PRAGMA journal_mode = WAL") # Melhora concorrência, evita lock
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, --  Trocado de BLOB pra TEXT
        role TEXT DEFAULT 'Dev' CHECK(role IN ('Dev', 'Admin')) --  Limita valores
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'Planejado' CHECK(status IN ('Planejado', 'Em Andamento', 'Concluído')),
        owner_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE --  FK: se deletar user, deleta projetos
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'A Fazer' CHECK(status IN ('A Fazer', 'Fazendo', 'Feito')),
        assigned_to INTEGER,
        project_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL, --  Se dev sai, task fica sem dono
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE --  Se deletar projeto, deleta tasks
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        user_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL -- 9. Mantém log mesmo se user for deletado
    )
    """)

    # 10. Índices pra performance. Sem isso, SELECT com 10k users fica lento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)")

    conn.commit()
    conn.close()