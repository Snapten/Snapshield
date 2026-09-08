from flask import Blueprint, jsonify

discord_bp = Blueprint('discord', __name__)

@discord_bp.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'online', 'platform': 'discord'})

@discord_bp.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'messages_today': 0,
        'moderation_actions': 0,
        'commands_used': 0
    })
