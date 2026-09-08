import discord
from discord.ext import commands
import sys
sys.path.append('..')
from database.models import db, Command

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commands_cache = {}
        self.load_commands_cache()
    
    def load_commands_cache(self):
        """Load all Discord commands into cache for quick access"""
        commands_db = Command.query.filter_by(platform='discord', enabled=True).all()
        for cmd in commands_db:
            self.commands_cache[cmd.name.lower()] = cmd
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Check for custom commands"""
        if message.author == self.bot.user:
            return
        
        if not message.content.startswith('!'):
            return
        
        args = message.content[1:].split()
        if not args:
            return
        
        cmd_name = args[0].lower()
        
        if cmd_name in self.commands_cache:
            await self.execute_command(message, cmd_name)
        
        await self.bot.process_commands(message)
    
    async def execute_command(self, message, cmd_name):
        """Execute a custom command"""
        cmd = self.commands_cache.get(cmd_name)
        if not cmd:
            return
        
        # Check permissions
        if not await self.check_permission(message, cmd.permission_level):
            await message.reply('You do not have permission to use this command!')
            return
        
        # Format response
        response = cmd.response.format(
            user=message.author.mention,
            username=message.author.name,
            server=message.guild.name if message.guild else 'DM'
        )
        
        try:
            await message.channel.send(response)
        except discord.Forbidden:
            await message.author.send(f'Could not send command response in {message.channel.mention}')
    
    async def check_permission(self, message, permission_level):
        """Check if user has permission to use command"""
        if permission_level == 'everyone':
            return True
        
        if permission_level == 'mod':
            return message.author.guild_permissions.moderate_members
        
        if permission_level == 'admin':
            return message.author.guild_permissions.administrator
        
        if permission_level == 'owner':
            return message.author == message.guild.owner
        
        return False
    
    @commands.command(name='addcmd')
    @commands.has_permissions(administrator=True)
    async def add_command(self, ctx, name: str, permission: str = 'everyone', *, response: str):
        """Add a new custom command (admin only)"""
        if permission not in ['everyone', 'mod', 'admin', 'owner']:
            await ctx.send('Invalid permission level! Use: everyone, mod, admin, owner')
            return
        
        # Check if command already exists
        existing = Command.query.filter_by(
            platform='discord',
            name=name.lower()
        ).first()
        
        if existing:
            await ctx.send(f'Command `!{name}` already exists!')
            return
        
        cmd = Command(
            platform='discord',
            name=name.lower(),
            response=response,
            permission_level=permission,
            enabled=True
        )
        db.session.add(cmd)
        db.session.commit()
        
        # Update cache
        self.commands_cache[name.lower()] = cmd
        
        await ctx.send(f'✅ Command `!{name}` created with permission level: **{permission}**')
    
    @commands.command(name='delcmd')
    @commands.has_permissions(administrator=True)
    async def delete_command(self, ctx, name: str):
        """Delete a custom command (admin only)"""
        cmd = Command.query.filter_by(
            platform='discord',
            name=name.lower()
        ).first()
        
        if not cmd:
            await ctx.send(f'Command `!{name}` not found!')
            return
        
        db.session.delete(cmd)
        db.session.commit()
        
        # Update cache
        if name.lower() in self.commands_cache:
            del self.commands_cache[name.lower()]
        
        await ctx.send(f'✅ Command `!{name}` deleted')
    
    @commands.command(name='listcmd')
    async def list_commands(self, ctx):
        """List all custom commands"""
        commands_db = Command.query.filter_by(platform='discord', enabled=True).all()
        
        if not commands_db:
            await ctx.send('No custom commands available')
            return
        
        embed = discord.Embed(
            title='Available Custom Commands',
            color=discord.Color.blue()
        )
        
        for cmd in commands_db:
            embed.add_field(
                name=f'!{cmd.name}',
                value=f'**Permission:** {cmd.permission_level}\n{cmd.response[:100]}...' if len(cmd.response) > 100 else f'**Permission:** {cmd.permission_level}\n{cmd.response}',
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
