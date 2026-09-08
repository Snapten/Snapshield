from flask import Blueprint, jsonify

twitch_bp = Blueprint('twitch', __name__)

@twitch_bp.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'online', 'platform': 'twitch'})

@twitch_bp.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'follows': 0,
        'moderation_actions': 0,
        'commands_used': 0
    })

@twitch_bp.route('/events', methods=['GET'])
def get_events():
    return jsonify({'events': []})
