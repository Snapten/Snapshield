from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='frontend', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///snapshield.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)
CORS(app)

# Import models
from models import *

# Import routes
from routes.auth import auth_bp
from routes.commands import commands_bp
from routes.moderation import moderation_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(commands_bp, url_prefix='/api/commands')
app.register_blueprint(moderation_bp, url_prefix='/api/moderation')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Serve frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return app.send_static_file(path)
    except:
        return app.send_static_file('index.html')

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
