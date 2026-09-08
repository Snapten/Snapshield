from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    session_token = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    discord_accounts = db.relationship('DiscordAccount', backref='user', lazy=True, cascade='all, delete-orphan')
    twitch_accounts = db.relationship('TwitchAccount', backref='user', lazy=True, cascade='all, delete-orphan')
    commands = db.relationship('Command', backref='user', lazy=True, cascade='all, delete-orphan')

class DiscordAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discord_id = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(500))
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500))
    is_bot = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TwitchAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    twitch_id = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(500))
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500))
    account_type = db.Column(db.String(50))  # 'streamer' or 'bot'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # 'discord' or 'twitch'
    name = db.Column(db.String(255), nullable=False)
    response = db.Column(db.Text, nullable=False)
    permission_level = db.Column(db.String(50), nullable=False)  # everyone, mod, vip, streamer
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserStrike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_user_id = db.Column(db.String(255), nullable=False)
    target_username = db.Column(db.String(255), nullable=False)
    strikes = db.Column(db.Integer, default=1)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModerationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # warn, kick, ban, mute
    target_user = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text)
    message_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModerationConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    strike_message = db.Column(db.Text)
    ban_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
