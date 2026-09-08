import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import sys
sys.path.insert(0, '..')

from database.models import db
from flask import Flask

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True

class SnapshieldBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.flask_app = None
    
    async def load_cogs(self):
        """Load all cogs from cogs directory"""
        cogs = ['moderation', 'commands', 'events']
        for cog in cogs:
            try:
                await self.load_extension(f'cogs.{cog}')
                print(f'✅ Loaded cog: {cog}')
            except Exception as e:
                print(f'❌ Failed to load cog {cog}: {e}')
    
    async def setup_hook(self):
        """Called when the bot is setting up"""
        await self.load_cogs()
    
    async def on_ready(self):
        """Called when the bot has successfully connected to Discord"""
        print(f'\n{'='*50}')
        print(f'✅ Snapshield Discord Bot Online')
        print(f'🎖️  Logged in as: {self.user}')
        print(f'🔗 Connected to {len(self.guilds)} server(s)')
        print(f'{'='*50}\n')
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='your server | !help'
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('❌ You do not have permission to use this command!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'❌ Missing required argument: {error.param}')
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(f'Unhandled error: {error}')
            await ctx.send(f'❌ An error occurred: {error}')

def create_bot():
    """Factory function to create bot instance"""
    return SnapshieldBot()

bot = create_bot()

# Run the bot
if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN not found in .env file')
        sys.exit(1)
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print('\n⏹️  Bot shutting down...')
