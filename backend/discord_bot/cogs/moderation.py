import discord
from discord.ext import commands
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from database.models import db, UserStrike, ModerationLog, ModerationConfig

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Log all messages"""
        if message.author == self.bot.user:
            return
        
        # Log message to database
        guild_id = message.guild.id if message.guild else None
        log = ModerationLog(
            platform='discord',
            action='message',
            target_user=str(message.author),
            message_content=message.content
        )
        db.session.add(log)
        db.session.commit()
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when members are kicked/banned"""
        audit_logs = await member.guild.audit_logs(limit=1).flatten()
        if audit_logs:
            entry = audit_logs[0]
            action = 'ban' if entry.action == discord.AuditLogAction.ban else 'kick'
            
            log = ModerationLog(
                platform='discord',
                action=action,
                target_user=str(member),
                reason=entry.reason or 'No reason provided'
            )
            db.session.add(log)
            db.session.commit()
    
    async def add_strike(self, user, reason='Unknown'):
        """Add strike to user and return total strikes"""
        strike = UserStrike(
            platform='discord',
            target_user_id=user.id,
            target_username=str(user),
            strikes=1,
            reason=reason
        )
        db.session.add(strike)
        db.session.commit()
        
        # Count total strikes
        total_strikes = UserStrike.query.filter_by(
            platform='discord',
            target_user_id=user.id
        ).count()
        
        return total_strikes
    
    @commands.command(name='warn')
    @commands.has_permissions(moderate_members=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason='No reason provided'):
        """Warn a user (adds a strike)"""
        if member == ctx.author:
            await ctx.send('You cannot warn yourself!')
            return
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send('You cannot warn this member!')
            return
        
        total_strikes = await self.add_strike(member, reason)
        
        # Get moderation config
        config = ModerationConfig.query.filter_by(
            platform='discord',
            enabled=True
        ).first()
        
        strike_msg = config.strike_message if config else f'{member.mention} has received a strike: {total_strikes}/3'
        strike_msg = strike_msg.format(user=member.mention, strikes=total_strikes)
        
        await ctx.send(strike_msg)
        
        # Log the strike
        log = ModerationLog(
            platform='discord',
            action='warn',
            target_user=str(member),
            reason=reason
        )
        db.session.add(log)
        db.session.commit()
        
        # Check if should ban
        if total_strikes >= 3:
            await self.ban_user_auto(ctx.guild, member, config)
    
    async def ban_user_auto(self, guild, member, config=None):
        """Auto-ban user after 3 strikes"""
        try:
            await guild.ban(member, reason='3-strike auto-ban')
            
            if config and config.ban_message:
                ban_msg = config.ban_message.format(user=member.mention)
            else:
                ban_msg = f'{member.mention} has been banned after 3 strikes'
            
            # Send to default channel
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(ban_msg)
                    break
            
            # Log the ban
            log = ModerationLog(
                platform='discord',
                action='ban',
                target_user=str(member),
                reason='3-strike auto-ban'
            )
            db.session.add(log)
            db.session.commit()
        except discord.Forbidden:
            print(f'Could not ban {member} - insufficient permissions')
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason='No reason provided'):
        """Kick a user from the server"""
        if member == ctx.author:
            await ctx.send('You cannot kick yourself!')
            return
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send('You cannot kick this member!')
            return
        
        try:
            await member.kick(reason=reason)
            await ctx.send(f'{member.mention} has been kicked. Reason: {reason}')
            
            # Log the kick
            log = ModerationLog(
                platform='discord',
                action='kick',
                target_user=str(member),
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
        except discord.Forbidden:
            await ctx.send('I do not have permission to kick this member!')
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason='No reason provided'):
        """Ban a user from the server"""
        if member == ctx.author:
            await ctx.send('You cannot ban yourself!')
            return
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send('You cannot ban this member!')
            return
        
        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.send(f'{member.mention} has been banned. Reason: {reason}')
            
            # Log the ban
            log = ModerationLog(
                platform='discord',
                action='ban',
                target_user=str(member),
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
        except discord.Forbidden:
            await ctx.send('I do not have permission to ban this member!')
    
    @commands.command(name='mute')
    @commands.has_permissions(moderate_members=True)
    async def mute_user(self, ctx, member: discord.Member, duration: int = 5, *, reason='No reason provided'):
        """Mute a user for specified minutes"""
        if member == ctx.author:
            await ctx.send('You cannot mute yourself!')
            return
        
        try:
            mute_until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(mute_until, reason=reason)
            await ctx.send(f'{member.mention} has been muted for {duration} minutes. Reason: {reason}')
            
            # Log the mute
            log = ModerationLog(
                platform='discord',
                action='mute',
                target_user=str(member),
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
        except discord.Forbidden:
            await ctx.send('I do not have permission to mute this member!')
    
    @commands.command(name='unmute')
    @commands.has_permissions(moderate_members=True)
    async def unmute_user(self, ctx, member: discord.Member):
        """Unmute a user"""
        try:
            await member.timeout(None, reason='Manual unmute')
            await ctx.send(f'{member.mention} has been unmuted')
        except discord.Forbidden:
            await ctx.send('I do not have permission to unmute this member!')
    
    @commands.command(name='strikes')
    async def check_strikes(self, ctx, member: discord.Member = None):
        """Check strikes for a user"""
        target = member or ctx.author
        
        strikes = UserStrike.query.filter_by(
            platform='discord',
            target_user_id=target.id
        ).all()
        
        total = len(strikes)
        embed = discord.Embed(
            title=f'Strikes for {target}',
            color=discord.Color.red() if total >= 2 else discord.Color.orange() if total == 1 else discord.Color.green()
        )
        embed.description = f'**Total Strikes: {total}/3**'
        
        for i, strike in enumerate(strikes, 1):
            embed.add_field(
                name=f'Strike {i}',
                value=f'**Reason:** {strike.reason}\n**Date:** {strike.created_at.strftime("%Y-%m-%d %H:%M")}',
                inline=False
            )
        
        if total == 0:
            embed.description = '**Total Strikes: 0/3** - This user is clean!'
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
