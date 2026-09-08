from flask import Blueprint, request, jsonify, session
from models import db, Command

commands_bp = Blueprint('commands', __name__)

@commands_bp.route('', methods=['GET'])
def get_commands():
    """Get all commands for user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    platform = request.args.get('platform')
    query = Command.query.filter_by(user_id=user_id)
    if platform:
        query = query.filter_by(platform=platform)
    
    commands = query.all()
    return jsonify([
        {
            'id': cmd.id,
            'name': cmd.name,
            'response': cmd.response,
            'permission_level': cmd.permission_level,
            'platform': cmd.platform,
            'enabled': cmd.enabled,
            'created_at': cmd.created_at.isoformat()
        } for cmd in commands
    ])

@commands_bp.route('', methods=['POST'])
def create_command():
    """Create new command"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    command = Command(
        user_id=user_id,
        platform=data.get('platform'),
        name=data.get('name'),
        response=data.get('response'),
        permission_level=data.get('permission_level', 'everyone'),
        enabled=data.get('enabled', True)
    )
    db.session.add(command)
    db.session.commit()
    
    return jsonify({
        'id': command.id,
        'name': command.name,
        'message': 'Command created successfully'
    }), 201

@commands_bp.route('/<int:cmd_id>', methods=['PUT'])
def update_command(cmd_id):
    """Update command"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    command = Command.query.get(cmd_id)
    if not command or command.user_id != user_id:
        return jsonify({'error': 'Command not found'}), 404
    
    data = request.json
    command.name = data.get('name', command.name)
    command.response = data.get('response', command.response)
    command.permission_level = data.get('permission_level', command.permission_level)
    command.enabled = data.get('enabled', command.enabled)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Command updated'})

@commands_bp.route('/<int:cmd_id>', methods=['DELETE'])
def delete_command(cmd_id):
    """Delete command"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    command = Command.query.get(cmd_id)
    if not command or command.user_id != user_id:
        return jsonify({'error': 'Command not found'}), 404
    
    db.session.delete(command)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Command deleted'})
