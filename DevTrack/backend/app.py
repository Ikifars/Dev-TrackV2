from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from dotenv import load_dotenv
import os

from database import init_db
import auth, projects, tasks

load_dotenv()

app = Flask(__name__)

# CORS: seguro e específico
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://ikifars.github.io"],  # Nunca usa "*"
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        # "supports_credentials": True  # Só liga se for usar cookie httpOnly
    }
})

# JWT: sem fallback inseguro. Se não tiver no .env, crasha.
jwt_secret = os.getenv("JWT_SECRET")
if not jwt_secret:
    raise ValueError("JWT_SECRET não definido no .env. Abortando.")

app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900  # 15min - bate com seu front
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 dias
jwt = JWTManager(app)

# Handlers de erro do JWT pra retornar JSON pro front
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Token expirado", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Token inválido", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Token de acesso necessário", "error": "authorization_required"}), 401

init_db()

app.register_blueprint(auth.bp, url_prefix='/api')
app.register_blueprint(projects.bp, url_prefix='/api')
app.register_blueprint(tasks.bp, url_prefix='/api')

@app.route('/')
def home():
    return {"status": "DevTrack API rodando - Production Ready"}

# 4. Handler de erro global pra não vazar stack trace
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Erro interno no servidor"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Rota não encontrada"}), 404

if __name__ == '__main__':
    # 5. DEBUG SEMPRE FALSE EM PROD. Render usa gunicorn, então isso aqui é só pra dev local.
    is_dev = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=5000, debug=is_dev)