from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DiscordAccount(db.Model):
    __tablename__ = 'discord_accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    discord_id = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    is_bot = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    access_token = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TwitchAccount(db.Model):
    __tablename__ = 'twitch_accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    twitch_id = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(50))  # 'streamer' or 'bot'
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Command Models
class Command(db.Model):
    __tablename__ = 'commands'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # 'discord' or 'twitch'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    response = db.Column(db.Text, nullable=False)
    permission_level = db.Column(db.String(50), nullable=False)  # everyone, mod, vip, streamer
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Moderation Models
class UserStrike(db.Model):
    __tablename__ = 'user_strikes'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_user_id = db.Column(db.String(255), nullable=False)  # Discord/Twitch user ID
    target_username = db.Column(db.String(255), nullable=False)
    strikes = db.Column(db.Integer, default=1)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModerationLog(db.Model):
    __tablename__ = 'moderation_logs'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'warn', 'kick', 'ban', 'mute'
    target_user = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text)
    message_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModerationConfig(db.Model):
    __tablename__ = 'moderation_config'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    strike_message = db.Column(db.Text)
    ban_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Event Models
class TwitchEvent(db.Model):
    __tablename__ = 'twitch_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'follow', 'subscribe', 'raid', etc.
    event_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
