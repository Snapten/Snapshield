import discord
from discord.ext import commands
import sys
sys.path.append('..')
from database.models import db, ModerationLog

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready():
        """Bot ready event"""
        print(f'\n✅ Discord Bot connected as {self.bot.user}')
        print(f'🔗 Connected to {len(self.bot.guilds)} server(s)')
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name='the server')
        )
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """When bot joins a new server"""
        print(f'📍 Joined new server: {guild.name} ({guild.id})')
        
        # Send welcome message
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title='Snapshield Bot',
                    description='Thank you for adding me! I\'m here to help with moderation and custom commands.',
                    color=discord.Color.blue()
                )
                embed.add_field(name='Getting Started', value='Use `!help` to see all commands')
                await channel.send(embed=embed)
                break
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """When a member joins the server"""
        log = ModerationLog(
            platform='discord',
            action='member_join',
            target_user=str(member),
            reason=f'User joined {member.guild.name}'
        )
        db.session.add(log)
        db.session.commit()
        print(f'👋 {member} joined {member.guild.name}')
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """When a member leaves the server"""
        log = ModerationLog(
            platform='discord',
            action='member_leave',
            target_user=str(member),
            reason=f'User left {member.guild.name}'
        )
        db.session.add(log)
        db.session.commit()
        print(f'👋 {member} left {member.guild.name}')
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """When a message is deleted"""
        if message.author == self.bot.user:
            return
        
        log = ModerationLog(
            platform='discord',
            action='message_delete',
            target_user=str(message.author),
            message_content=message.content,
            reason=f'Message deleted from {message.channel}'
        )
        db.session.add(log)
        db.session.commit()
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """When a message is edited"""
        if before.author == self.bot.user:
            return
        
        if before.content == after.content:
            return
        
        log = ModerationLog(
            platform='discord',
            action='message_edit',
            target_user=str(before.author),
            message_content=f'Before: {before.content}\nAfter: {after.content}',
            reason=f'Message edited in {before.channel}'
        )
        db.session.add(log)
        db.session.commit()
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """When a member's profile is updated"""
        if before.roles != after.roles:
            removed_roles = set(before.roles) - set(after.roles)
            added_roles = set(after.roles) - set(before.roles)
            
            if removed_roles or added_roles:
                log = ModerationLog(
                    platform='discord',
                    action='roles_updated',
                    target_user=str(after),
                    reason=f'Roles changed: Removed {[r.name for r in removed_roles]}, Added {[r.name for r in added_roles]}'
                )
                db.session.add(log)
                db.session.commit()

async def setup(bot):
    await bot.add_cog(Events(bot))
