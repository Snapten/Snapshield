from flask import Blueprint, request, jsonify, session, redirect
from models import db, User, DiscordAccount, TwitchAccount
import requests
import os
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

DISCORD_API = 'https://discord.com/api/v10'
TWITCH_API = 'https://id.twitch.tv/oauth2/token'

@auth_bp.route('/discord/login', methods=['POST'])
def discord_login():
    """Initiate Discord OAuth flow"""
    client_id = os.getenv('DISCORD_CLIENT_ID')
    redirect_uri = os.getenv('DISCORD_REDIRECT_URI')
    
    oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=identify%20email%20guilds"
    )
    
    return jsonify({'auth_url': oauth_url})

@auth_bp.route('/discord/callback', methods=['GET'])
def discord_callback():
    """Handle Discord OAuth callback"""
    code = request.args.get('code')
    if not code:
        return redirect('/?error=no_code')
    
    try:
        # Exchange code for token
        token_response = requests.post(
            f'{DISCORD_API}/oauth2/token',
            data={
                'client_id': os.getenv('DISCORD_CLIENT_ID'),
                'client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': os.getenv('DISCORD_REDIRECT_URI')
            }
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        
        # Get user info
        user_response = requests.get(
            f'{DISCORD_API}/users/@me',
            headers={'Authorization': f'Bearer {token_data["access_token"]}'}
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Find or create user
        discord_account = DiscordAccount.query.filter_by(
            discord_id=user_data['id']
        ).first()
        
        if discord_account:
            discord_account.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                discord_account.refresh_token = token_data['refresh_token']
            user = discord_account.user
        else:
            user = User.query.filter_by(email=user_data.get('email')).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data.get('email')
                )
                db.session.add(user)
                db.session.flush()
            
            discord_account = DiscordAccount(
                user_id=user.id,
                discord_id=user_data['id'],
                username=user_data['username'],
                avatar=user_data.get('avatar'),
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                is_default=True
            )
            db.session.add(discord_account)
        
        session['user_id'] = user.id
        session['discord_account_id'] = discord_account.id
        db.session.commit()
        
        return redirect('/?discord_success=true')
    except Exception as e:
        return redirect(f'/?error={str(e)}')

@auth_bp.route('/twitch/login', methods=['POST'])
def twitch_login():
    """Initiate Twitch OAuth flow"""
    client_id = os.getenv('TWITCH_CLIENT_ID')
    redirect_uri = os.getenv('TWITCH_REDIRECT_URI')
    
    oauth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=user:read:email%20moderation:read"
    )
    
    return jsonify({'auth_url': oauth_url})

@auth_bp.route('/twitch/callback', methods=['GET'])
def twitch_callback():
    """Handle Twitch OAuth callback"""
    code = request.args.get('code')
    if not code:
        return redirect('/?error=no_code')
    
    try:
        token_response = requests.post(
            TWITCH_API,
            data={
                'client_id': os.getenv('TWITCH_CLIENT_ID'),
                'client_secret': os.getenv('TWITCH_CLIENT_SECRET'),
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': os.getenv('TWITCH_REDIRECT_URI')
            }
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        
        user_response = requests.get(
            'https://api.twitch.tv/helix/users',
            headers={
                'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
                'Authorization': f'Bearer {token_data["access_token"]}'
            }
        )
        user_response.raise_for_status()
        users = user_response.json()['data']
        if not users:
            return redirect('/?error=no_user_data')
        
        user_data = users[0]
        
        twitch_account = TwitchAccount.query.filter_by(
            twitch_id=user_data['id']
        ).first()
        
        if twitch_account:
            twitch_account.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                twitch_account.refresh_token = token_data['refresh_token']
            user = twitch_account.user
        else:
            user = User.query.filter_by(email=user_data.get('email')).first()
            if not user:
                user = User(
                    username=user_data['login'],
                    email=user_data.get('email')
                )
                db.session.add(user)
                db.session.flush()
            
            twitch_account = TwitchAccount(
                user_id=user.id,
                twitch_id=user_data['id'],
                username=user_data['login'],
                avatar=user_data.get('profile_image_url'),
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                account_type='streamer'
            )
            db.session.add(twitch_account)
        
        session['user_id'] = user.id
        session['twitch_account_id'] = twitch_account.id
        db.session.commit()
        
        return redirect('/?twitch_success=true')
    except Exception as e:
        return redirect(f'/?error={str(e)}')

@auth_bp.route('/user', methods=['GET'])
def get_user():
    """Get current user info"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'discord_accounts': [
            {
                'id': acc.id,
                'username': acc.username,
                'avatar': acc.avatar,
                'is_default': acc.is_default
            } for acc in user.discord_accounts
        ],
        'twitch_accounts': [
            {
                'id': acc.id,
                'username': acc.username,
                'avatar': acc.avatar,
                'account_type': acc.account_type
            } for acc in user.twitch_accounts
        ]
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})
