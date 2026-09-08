import asyncio
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationContext
from twitchAPI.chat import Chat, EventData
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, '..')

from database.models import db, Command, UserStrike, ModerationLog, TwitchEvent

load_dotenv()

class SnapshieldTwitchBot:
    def __init__(self):
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.twitch = None
        self.chat = None
        self.streamer_user = None
        self.bot_user = None
        self.commands_cache = {}
    
    async def initialize(self):
        """Initialize Twitch API and Chat connections"""
        try:
            self.twitch = await Twitch(self.client_id, self.client_secret)
            print('✅ Twitch API initialized')
            
            # Load commands cache
            self.load_commands_cache()
            print('✅ Commands cache loaded')
        except Exception as e:
            print(f'❌ Failed to initialize Twitch API: {e}')
            return False
        
        return True
    
    def load_commands_cache(self):
        """Load all Twitch commands into cache"""
        commands_db = Command.query.filter_by(platform='twitch', enabled=True).all()
        for cmd in commands_db:
            self.commands_cache[cmd.name.lower()] = cmd
        print(f'📦 Loaded {len(self.commands_cache)} commands')
    
    async def setup_chat(self, channel_name, bot_name):
        """Setup chat connection"""
        try:
            self.chat = await Chat(self.twitch)
            
            # Set event handlers
            self.chat.register_on_ready(self.on_ready)
            self.chat.register_on_message(self.on_message)
            self.chat.register_on_follow(self.on_follow)
            self.chat.register_on_subscribe(self.on_subscribe)
            self.chat.register_on_raid(self.on_raid)
            self.chat.register_on_bits(self.on_bits)
            self.chat.register_on_join(self.on_join)
            
            await self.chat.start()
            print(f'✅ Chat connected for {channel_name}')
        except Exception as e:
            print(f'❌ Failed to setup chat: {e}')
    
    async def on_ready(self, ready_message: EventData):
        """Called when chat is ready"""
        print(f'🟢 Twitch Chat Ready - {ready_message.data_to_str()}')
    
    async def on_message(self, msg: EventData):
        """Handle incoming chat messages"""
        try:
            user = msg.chatter_user_name
            message = msg.message.text
            
            # Log message
            log = ModerationLog(
                platform='twitch',
                action='message',
                target_user=user,
                message_content=message
            )
            db.session.add(log)
            db.session.commit()
            
            # Check for commands
            if message.startswith('!'):
                await self.handle_command(msg, user, message)
        except Exception as e:
            print(f'❌ Error handling message: {e}')
    
    async def handle_command(self, msg, user, message):
        """Handle custom commands"""
        try:
            parts = message[1:].split()
            if not parts:
                return
            
            cmd_name = parts[0].lower()
            
            if cmd_name not in self.commands_cache:
                return
            
            cmd = self.commands_cache[cmd_name]
            
            # Check permissions
            if not await self.check_permission(msg, cmd.permission_level):
                await self.chat.send_message(
                    msg.room_id,
                    f'@{user} You do not have permission to use this command!'
                )
                return
            
            # Format and send response
            response = cmd.response.format(
                user=user,
                args=' '.join(parts[1:]) if len(parts) > 1 else ''
            )
            
            await self.chat.send_message(msg.room_id, response)
        except Exception as e:
            print(f'❌ Error handling command: {e}')
    
    async def check_permission(self, msg, permission_level):
        """Check if user has permission for command"""
        if permission_level == 'everyone':
            return True
        
        if permission_level == 'vip' and msg.user_type.value == 'VIP':
            return True
        
        if permission_level == 'mod':
            return msg.user_type.value in ['MODERATOR', 'BROADCASTER']
        
        if permission_level == 'streamer':
            return msg.user_type.value == 'BROADCASTER'
        
        return False
    
    async def on_follow(self, msg: EventData):
        """Handle new followers"""
        try:
            follower = msg.user_name
            print(f'👥 New follow: {follower}')
            
            event = TwitchEvent(
                user_id=1,  # Should be updated to actual user
                event_type='follow',
                event_data={
                    'user': follower,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(event)
            db.session.commit()
            
            # Send follow message
            await self.chat.send_message(
                msg.room_id,
                f'🎉 Thanks for the follow {follower}! Welcome to the community!'
            )
        except Exception as e:
            print(f'❌ Error handling follow: {e}')
    
    async def on_subscribe(self, msg: EventData):
        """Handle subscriptions"""
        try:
            subscriber = msg.user_name
            tier = msg.subscription_tier or 'tier'
            print(f'🎁 New subscriber: {subscriber} ({tier})')
            
            event = TwitchEvent(
                user_id=1,
                event_type='subscribe',
                event_data={
                    'user': subscriber,
                    'tier': tier,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(event)
            db.session.commit()
            
            await self.chat.send_message(
                msg.room_id,
                f'🎉 Welcome to the sub squad {subscriber}! Thank you for subscribing!'
            )
        except Exception as e:
            print(f'❌ Error handling subscribe: {e}')
    
    async def on_raid(self, msg: EventData):
        """Handle raids"""
        try:
            raider = msg.user_name
            viewers = msg.raid_viewer_count or '?'
            print(f'⚔️ Raid from {raider} ({viewers} viewers)')
            
            event = TwitchEvent(
                user_id=1,
                event_type='raid',
                event_data={
                    'user': raider,
                    'viewers': viewers,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(event)
            db.session.commit()
            
            await self.chat.send_message(
                msg.room_id,
                f'⚔️ Thanks for the raid {raider}! Welcome everyone!'
            )
        except Exception as e:
            print(f'❌ Error handling raid: {e}')
    
    async def on_bits(self, msg: EventData):
        """Handle bits/cheers"""
        try:
            user = msg.user_name
            bits = msg.bits_used or 0
            print(f'💎 {user} cheered {bits} bits')
            
            event = TwitchEvent(
                user_id=1,
                event_type='bits',
                event_data={
                    'user': user,
                    'bits': bits,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(event)
            db.session.commit()
            
            await self.chat.send_message(
                msg.room_id,
                f'💎 Thanks {user} for the {bits} bits! You rock!'
            )
        except Exception as e:
            print(f'❌ Error handling bits: {e}')
    
    async def on_join(self, msg: EventData):
        """Handle user joins"""
        print(f'📍 {msg.user_name} joined chat')
    
    async def add_strike(self, user, reason='Unknown'):
        """Add strike to Twitch user"""
        strike = UserStrike(
            platform='twitch',
            target_user_id=user,
            target_username=user,
            strikes=1,
            reason=reason
        )
        db.session.add(strike)
        db.session.commit()
        
        total_strikes = UserStrike.query.filter_by(
            platform='twitch',
            target_user_id=user
        ).count()
        
        return total_strikes
    
    async def ban_user(self, channel_id, user, reason):
        """Ban user from channel"""
        try:
            # This would require moderator token
            print(f'🚫 Banning {user} for: {reason}')
            
            log = ModerationLog(
                platform='twitch',
                action='ban',
                target_user=user,
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f'❌ Error banning user: {e}')
    
    async def run(self):
        """Run the bot"""
        if not await self.initialize():
            return
        
        try:
            # Setup chat connection
            # These would come from database/config
            channel_name = os.getenv('TWITCH_CHANNEL')
            bot_name = os.getenv('TWITCH_BOT_NAME')
            
            if channel_name and bot_name:
                await self.setup_chat(channel_name, bot_name)
                print('\n' + '='*50)
                print('✅ Snapshield Twitch Bot Online')
                print(f'📺 Channel: {channel_name}')
                print(f'🤖 Bot: {bot_name}')
                print('='*50 + '\n')
                
                # Keep running
                await asyncio.Event().wait()
            else:
                print('❌ TWITCH_CHANNEL or TWITCH_BOT_NAME not configured')
        except KeyboardInterrupt:
            print('\n⏹️  Bot shutting down...')
            if self.chat:
                await self.chat.stop()
        except Exception as e:
            print(f'❌ Error: {e}')

if __name__ == '__main__':
    bot = SnapshieldTwitchBot()
    asyncio.run(bot.run())
