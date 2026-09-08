from flask import Blueprint, request, jsonify
from database.models import db, UserStrike, ModerationLog, ModerationConfig

moderation_bp = Blueprint('moderation', __name__)

@moderation_bp.route('/config/<platform>', methods=['GET'])
def get_moderation_config(platform):
    config = ModerationConfig.query.filter_by(platform=platform).first()
    if not config:
        return jsonify({'enabled': True, 'strike_message': '', 'ban_message': ''})
    
    return jsonify({
        'enabled': config.enabled,
        'strike_message': config.strike_message,
        'ban_message': config.ban_message
    })

@moderation_bp.route('/config/<platform>', methods=['POST'])
def update_moderation_config(platform):
    data = request.json
    config = ModerationConfig.query.filter_by(platform=platform).first()
    
    if not config:
        config = ModerationConfig(platform=platform)
    
    config.enabled = data.get('enabled', config.enabled)
    config.strike_message = data.get('strike_message', config.strike_message)
    config.ban_message = data.get('ban_message', config.ban_message)
    
    db.session.add(config)
    db.session.commit()
    return jsonify({'status': 'success'})

@moderation_bp.route('/strike', methods=['POST'])
def add_strike():
    data = request.json
    strike = UserStrike(
        platform=data.get('platform'),
        target_user_id=data.get('target_user_id'),
        target_username=data.get('target_username'),
        strikes=data.get('strikes', 1),
        reason=data.get('reason')
    )
    db.session.add(strike)
    db.session.commit()
    
    # Check if 3 strikes reached
    total_strikes = UserStrike.query.filter_by(
        target_user_id=data.get('target_user_id')
    ).count()
    
    return jsonify({
        'status': 'success',
        'total_strikes': total_strikes,
        'should_ban': total_strikes >= 3
    })

@moderation_bp.route('/logs/<platform>', methods=['GET'])
def get_moderation_logs(platform):
    logs = ModerationLog.query.filter_by(platform=platform).order_by(
        ModerationLog.created_at.desc()
    ).limit(50).all()
    
    return jsonify({
        'logs': [
            {
                'id': log.id,
                'action': log.action,
                'target_user': log.target_user,
                'reason': log.reason,
                'timestamp': log.created_at.isoformat()
            } for log in logs
        ]
    })
