from flask import Blueprint, request, jsonify, session
from models import db, ModerationLog, UserStrike, ModerationConfig

moderation_bp = Blueprint('moderation', __name__)

@moderation_bp.route('/config', methods=['GET'])
def get_config():
    """Get moderation config"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    platform = request.args.get('platform')
    config = ModerationConfig.query.filter_by(user_id=user_id, platform=platform).first()
    
    if not config:
        return jsonify({
            'enabled': True,
            'strike_message': 'User has received a strike: {strikes}/3',
            'ban_message': 'User has been banned after 3 strikes'
        })
    
    return jsonify({
        'id': config.id,
        'enabled': config.enabled,
        'strike_message': config.strike_message,
        'ban_message': config.ban_message
    })

@moderation_bp.route('/config', methods=['POST'])
def update_config():
    """Update moderation config"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    platform = data.get('platform')
    
    config = ModerationConfig.query.filter_by(user_id=user_id, platform=platform).first()
    if not config:
        config = ModerationConfig(user_id=user_id, platform=platform)
        db.session.add(config)
    
    config.enabled = data.get('enabled', config.enabled)
    config.strike_message = data.get('strike_message', config.strike_message)
    config.ban_message = data.get('ban_message', config.ban_message)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Config updated'})

@moderation_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get moderation logs"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    platform = request.args.get('platform')
    limit = request.args.get('limit', 50, type=int)
    
    logs = ModerationLog.query.filter_by(user_id=user_id, platform=platform).order_by(
        ModerationLog.created_at.desc()
    ).limit(limit).all()
    
    return jsonify([
        {
            'id': log.id,
            'action': log.action,
            'target_user': log.target_user,
            'reason': log.reason,
            'message_content': log.message_content,
            'created_at': log.created_at.isoformat()
        } for log in logs
    ])

@moderation_bp.route('/strike', methods=['POST'])
def add_strike():
    """Add strike to user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    strike = UserStrike(
        user_id=user_id,
        platform=data.get('platform'),
        target_user_id=data.get('target_user_id'),
        target_username=data.get('target_username'),
        reason=data.get('reason')
    )
    db.session.add(strike)
    db.session.commit()
    
    total = UserStrike.query.filter_by(
        user_id=user_id,
        platform=data.get('platform'),
        target_user_id=data.get('target_user_id')
    ).count()
    
    return jsonify({
        'success': True,
        'total_strikes': total,
        'should_ban': total >= 3
    }), 201
