from flask import Blueprint, request, jsonify
from database.models import db, Command

commands_bp = Blueprint('commands', __name__)

@commands_bp.route('/create', methods=['POST'])
def create_command():
    data = request.json
    command = Command(
        platform=data.get('platform'),
        name=data.get('name'),
        response=data.get('response'),
        permission_level=data.get('permission_level'),
        enabled=data.get('enabled', True)
    )
    db.session.add(command)
    db.session.commit()
    return jsonify({'status': 'success', 'command_id': command.id})

@commands_bp.route('/<platform>', methods=['GET'])
def get_commands(platform):
    commands = Command.query.filter_by(platform=platform).all()
    return jsonify({
        'commands': [
            {
                'id': cmd.id,
                'name': cmd.name,
                'response': cmd.response,
                'permission_level': cmd.permission_level,
                'enabled': cmd.enabled
            } for cmd in commands
        ]
    })

@commands_bp.route('/<command_id>/update', methods=['PUT'])
def update_command(command_id):
    command = Command.query.get(command_id)
    if not command:
        return jsonify({'error': 'Command not found'}), 404
    
    data = request.json
    command.name = data.get('name', command.name)
    command.response = data.get('response', command.response)
    command.permission_level = data.get('permission_level', command.permission_level)
    command.enabled = data.get('enabled', command.enabled)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@commands_bp.route('/<command_id>/delete', methods=['DELETE'])
def delete_command(command_id):
    command = Command.query.get(command_id)
    if not command:
        return jsonify({'error': 'Command not found'}), 404
    
    db.session.delete(command)
    db.session.commit()
    return jsonify({'status': 'success'})
