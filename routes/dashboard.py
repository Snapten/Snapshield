from flask import Blueprint, jsonify, session
from models import User, ModerationLog, Command, UserStrike

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard stats"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    discord_logs = ModerationLog.query.filter_by(user_id=user_id, platform='discord').count()
    twitch_logs = ModerationLog.query.filter_by(user_id=user_id, platform='twitch').count()
    
    return jsonify({
        'username': user.username,
        'discord_accounts': len(user.discord_accounts),
        'twitch_accounts': len(user.twitch_accounts),
        'total_commands': len(user.commands),
        'discord_moderation_logs': discord_logs,
        'twitch_moderation_logs': twitch_logs,
        'member_since': user.created_at.isoformat()
    })
