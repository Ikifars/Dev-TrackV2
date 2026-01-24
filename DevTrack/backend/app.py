from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from database import init_db
import auth, projects, tasks

load_dotenv()

app = Flask(__name__)

#CORS(app, origins=["https://ikifars.github.io/Dev-TrackV2/"])
CORS(app, resources={r"/api/*": {
    "origins": ["https://ikifars.github.io"]
}})


app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET", "devtrack-dev")
jwt = JWTManager(app)

init_db()

app.register_blueprint(auth.bp, url_prefix='/api')
app.register_blueprint(projects.bp, url_prefix='/api')
app.register_blueprint(tasks.bp, url_prefix='/api')

@app.route('/')
def home():
    return {"status": "DevTrack API rodando - Production Ready"}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
