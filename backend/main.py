from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///snapshield.db')
db = SQLAlchemy(app)

# Import blueprints
from discord_bot.api import discord_bp
from twitch_bot.api import twitch_bp
from api.auth import auth_bp
from api.commands import commands_bp
from api.moderation import moderation_bp

# Register blueprints
app.register_blueprint(discord_bp, url_prefix='/api/discord')
app.register_blueprint(twitch_bp, url_prefix='/api/twitch')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(commands_bp, url_prefix='/api/commands')
app.register_blueprint(moderation_bp, url_prefix='/api/moderation')

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Snapshield API'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
