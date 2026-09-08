import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class DiscordBot:
    def __init__(self):
        self.bot = bot
        self.load_cogs()
    
    def load_cogs(self):
        # Load moderation and command cogs
        pass
    
    def run(self):
        token = os.getenv('DISCORD_TOKEN')
        self.bot.run(token)

@bot.event
async def on_ready():
    print(f'Discord Bot logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Log message
    print(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message)

if __name__ == '__main__':
    discord_bot = DiscordBot()
    discord_bot.run()
