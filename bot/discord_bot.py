"""
bot/discord_bot.py

The core discord.py client used by SnapShield. All moderation logic
(word filters, strikes, auto roles, reaction roles, logging) lives here.
The bot reads/writes its configuration through the shared DataManager so
that changes made in the desktop UI take effect immediately, and events
are reported back to the UI via a callback object (see bot/bot_thread.py).
"""

from __future__ import annotations

import datetime
import logging
import time
from typing import Callable, Optional

import aiohttp
import discord
from discord.ext import commands, tasks

from storage.json_store import DataManager

logger = logging.getLogger("snapshield.bot")

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"
TWITCH_USERS_URL = "https://api.twitch.tv/helix/users"


class ModerationBot(commands.Bot):
    """
    Discord client with SnapShield's moderation behaviour wired in.

    `events` is a simple object exposing `.emit(event_name: str, **kwargs)`
    that the UI layer uses to receive status updates without discord.py
    needing to know anything about Qt.
    """

    def __init__(self, data: DataManager, emit: Callable[..., None], guild_id: Optional[int] = None):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        intents.reactions = True

        super().__init__(command_prefix="!snapshield-unused-", intents=intents)

        self.data = data
        self.emit = emit
        self.target_guild_id = guild_id
        self._background_tasks_started = False
        self._current_reset_hours = 12
        self.session: Optional[aiohttp.ClientSession] = None
        self._twitch_token: Optional[str] = None
        self._twitch_token_expiry: float = 0.0

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    async def setup_hook(self) -> None:
        logger.info("Bot setup hook running.")
        self.session = aiohttp.ClientSession()

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "?")
        self.emit("status", online=True, message=f"Connected as {self.user}")
        await self._refresh_guild_snapshot()
        self._start_background_tasks()

    async def on_resumed(self) -> None:
        """Fired when discord.py transparently resumes a dropped gateway
        session. We treat this the same as a fresh connect for the UI."""
        logger.info("Gateway session resumed.")
        self.emit("status", online=True, message="Reconnected to Discord")
        self._start_background_tasks()

    async def on_disconnect(self) -> None:
        self.emit("status", online=False, message="Disconnected from Discord")

    async def on_error(self, event_method, *args, **kwargs):  # noqa: D401
        logger.exception("Unhandled error in event %s", event_method)
        self.emit("error", message=f"Error in {event_method}")

    async def close(self) -> None:
        if self.keep_alive_task.is_running():
            self.keep_alive_task.cancel()
        if self.strike_reset_task.is_running():
            self.strike_reset_task.cancel()
        if self.twitch_check_task.is_running():
            self.twitch_check_task.cancel()
        if self.session and not self.session.closed:
            await self.session.close()
        await super().close()

    def _start_background_tasks(self) -> None:
        """Start the keep-alive handshake loop and the strike-reset loop
        exactly once, even across reconnects/resumes. The reset loop's
        interval is read from config at start time; use
        `refresh_strike_reset_schedule()` to apply a change live."""
        if self._background_tasks_started:
            return
        self._background_tasks_started = True
        if not self.keep_alive_task.is_running():
            self.keep_alive_task.start()
        if not self.strike_reset_task.is_running():
            strikes_cfg = self.data.strikes.load()
            self._current_reset_hours = max(1, int(strikes_cfg.get("auto_reset_hours", 12) or 12))
            self.strike_reset_task.change_interval(hours=self._current_reset_hours)
            self.strike_reset_task.start()
        if not self.twitch_check_task.is_running():
            self.twitch_check_task.start()

    # ------------------------------------------------------------------ #
    # Keep-alive / handshake
    # ------------------------------------------------------------------ #
    @tasks.loop(minutes=5)
    async def keep_alive_task(self) -> None:
        """
        Lightweight periodic handshake so long-running sessions don't go
        stale and silently drop offline. discord.py's gateway already
        heartbeats automatically; this loop adds an extra safety net by
        touching the connection (a cheap presence refresh) on a schedule
        and re-asserting bot status for the UI.
        """
        if not self.is_ready() or self.is_closed():
            return
        try:
            await self.change_presence(status=discord.Status.online, activity=discord.Game("Moderating the server"))
            logger.debug("Keep-alive handshake sent.")
            self.emit("status", online=True, message="Keep-alive handshake OK")
        except discord.HTTPException as exc:
            logger.warning("Keep-alive handshake failed: %s", exc)

    @keep_alive_task.before_loop
    async def _before_keep_alive(self) -> None:
        await self.wait_until_ready()

    # ------------------------------------------------------------------ #
    # Automatic strike reset (interval + on/off are user-configurable)
    # ------------------------------------------------------------------ #
    @tasks.loop(hours=12)
    async def strike_reset_task(self) -> None:
        strikes_cfg = self.data.strikes.load()
        if not strikes_cfg.get("auto_reset_enabled", True):
            logger.debug("Automatic strike reset skipped (disabled in settings).")
            return
        cleared = len(strikes_cfg.get("user_strikes", {}))
        self.data.strikes.update(lambda d: {**d, "user_strikes": {}})
        hours = strikes_cfg.get("auto_reset_hours", 12)
        logger.info("Automatic strike reset ran: cleared %d user(s).", cleared)
        self._log_event("strikes", f"Automatic {hours}-hour strike reset cleared {cleared} user(s).")

    @strike_reset_task.before_loop
    async def _before_strike_reset(self) -> None:
        await self.wait_until_ready()

    async def refresh_strike_reset_schedule(self) -> None:
        """Re-read the configured reset interval/enabled flag and apply
        any interval change immediately, without requiring a reconnect.
        The enabled/disabled flag is checked fresh on every tick inside
        the loop body, so toggling it takes effect on the very next run
        regardless of whether this method is called."""
        strikes_cfg = self.data.strikes.load()
        hours = max(1, int(strikes_cfg.get("auto_reset_hours", 12) or 12))
        if hours != self._current_reset_hours:
            self._current_reset_hours = hours
            self.strike_reset_task.change_interval(hours=hours)
            logger.info("Strike reset interval updated to %d hour(s).", hours)

    # ------------------------------------------------------------------ #
    # Social Notifications: Twitch "went live" alerts, posted as embeds
    # ------------------------------------------------------------------ #
    async def _get_twitch_token(self, client_id: str, client_secret: str) -> Optional[str]:
        """Fetch (and cache) a Twitch app access token via the client
        credentials flow. Cached until ~60 seconds before it expires."""
        if self._twitch_token and time.time() < self._twitch_token_expiry - 60:
            return self._twitch_token
        if not self.session:
            return None
        try:
            async with self.session.post(
                TWITCH_TOKEN_URL,
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                },
            ) as resp:
                if resp.status != 200:
                    self.emit("error", message="Twitch authentication failed. Check your Client ID/Secret.")
                    return None
                payload = await resp.json()
        except aiohttp.ClientError as exc:
            logger.warning("Twitch auth request failed: %s", exc)
            return None

        self._twitch_token = payload.get("access_token")
        self._twitch_token_expiry = time.time() + float(payload.get("expires_in", 3600))
        return self._twitch_token

    async def _fetch_twitch_streams(self, client_id: str, token: str, usernames: list) -> dict:
        """Query Twitch's Helix `/streams` endpoint for the given logins.
        Returns a dict keyed by lowercase username, present only for
        channels that are currently live."""
        if not usernames or not self.session:
            return {}
        headers = {"Client-Id": client_id, "Authorization": f"Bearer {token}"}
        params = [("user_login", u) for u in usernames[:100]]
        try:
            async with self.session.get(TWITCH_STREAMS_URL, headers=headers, params=params) as resp:
                if resp.status == 401:
                    # Token expired/was revoked -- drop it so the next
                    # cycle re-authenticates instead of looping on 401s.
                    self._twitch_token = None
                    self.emit("error", message="Twitch token was rejected; re-authenticating next cycle.")
                    return {}
                if resp.status != 200:
                    self.emit("error", message=f"Twitch API returned {resp.status} while checking live status.")
                    return {}
                payload = await resp.json()
        except aiohttp.ClientError as exc:
            logger.warning("Twitch streams request failed: %s", exc)
            return {}
        return {item["user_login"].lower(): item for item in payload.get("data", [])}

    async def _fetch_twitch_user(self, client_id: str, token: str, username: str) -> Optional[dict]:
        """Look up a Twitch account's profile (avatar, display name) via
        the Helix `/users` endpoint -- used to give the notification
        embed the streamer's actual avatar and proper display-name
        casing, the way Sapphire's Twitch alerts do."""
        if not self.session:
            return None
        headers = {"Client-Id": client_id, "Authorization": f"Bearer {token}"}
        try:
            async with self.session.get(TWITCH_USERS_URL, headers=headers, params={"login": username}) as resp:
                if resp.status != 200:
                    return None
                payload = await resp.json()
        except aiohttp.ClientError as exc:
            logger.warning("Twitch user lookup failed: %s", exc)
            return None
        items = payload.get("data", [])
        return items[0] if items else None

    @staticmethod
    def _build_twitch_embed(subscription: dict, stream: dict, user_info: Optional[dict]) -> discord.Embed:
        """Build the 'went live' notification as an embed styled after
        Sapphire's Twitch alerts: streamer avatar, a large stream
        preview thumbnail, game, and viewer count. A custom message
        template is optional; {username}/{title}/{game} tokens are
        substituted in if the user supplied one."""
        username = subscription.get("twitch_username", "")
        display_name = (user_info or {}).get("display_name") or username
        avatar_url = (user_info or {}).get("profile_image_url")
        stream_title = stream.get("title", "")
        game_name = stream.get("game_name") or "Unknown"
        viewers = stream.get("viewer_count", 0)

        template = (subscription.get("message_template") or "").strip()
        if template:
            description = (
                template.replace("{username}", display_name)
                .replace("{title}", stream_title)
                .replace("{game}", game_name)
            )
        else:
            description = stream_title or f"{display_name} just went live!"

        embed = discord.Embed(
            title=f"🔴 {display_name} is now live on Twitch!",
            description=description,
            color=discord.Color(0x9146FF),  # Twitch purple
            url=f"https://twitch.tv/{username}",
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Game", value=game_name, inline=True)
        embed.add_field(name="Viewers", value=str(viewers), inline=True)

        thumbnail_url = stream.get("thumbnail_url", "")
        if thumbnail_url:
            # Twitch caches thumbnail URLs aggressively and Discord caches
            # whatever it fetches once -- append a cache-busting query
            # param (Sapphire does the same) so a *new* stream session's
            # preview doesn't show a stale cached image.
            resized = thumbnail_url.replace("{width}", "1280").replace("{height}", "720")
            embed.set_image(url=f"{resized}?t={int(time.time())}")

        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        embed.set_author(
            name="Twitch",
            icon_url="https://static-cdn.jtvnw.net/ttv-boxart/twitch-logo.png",
            url=f"https://twitch.tv/{username}",
        )
        embed.set_footer(text="Live notification via SnapShield")
        return embed

    @tasks.loop(minutes=2)
    async def twitch_check_task(self) -> None:
        social_cfg = self.data.social_notifications.load()
        client_id = social_cfg.get("twitch_client_id", "").strip()
        client_secret = social_cfg.get("twitch_client_secret", "").strip()
        subscriptions = social_cfg.get("subscriptions", [])
        if not client_id or not client_secret or not subscriptions:
            return

        token = await self._get_twitch_token(client_id, client_secret)
        if not token:
            return

        usernames = [s["twitch_username"] for s in subscriptions if s.get("twitch_username")]
        live_map = await self._fetch_twitch_streams(client_id, token, usernames)

        updated = []
        for sub in subscriptions:
            username_lower = sub.get("twitch_username", "").lower()
            stream = live_map.get(username_lower)
            was_live = sub.get("is_live", False)
            channel = self.get_channel(int(sub["discord_channel_id"])) if sub.get("discord_channel_id") else None

            if stream and (not was_live or stream.get("id") != sub.get("last_stream_id")):
                # Newly live (or a new stream session under the same
                # account) -- post the notification.
                message_id = sub.get("last_message_id")
                if channel:
                    user_info = await self._fetch_twitch_user(client_id, token, sub["twitch_username"])
                    embed = self._build_twitch_embed(sub, stream, user_info)
                    role_id = sub.get("role_id")
                    content = f"<@&{role_id}>" if role_id else None
                    mentions = discord.AllowedMentions(roles=True) if role_id else discord.AllowedMentions.none()
                    try:
                        message = await channel.send(content=content, embed=embed, allowed_mentions=mentions)
                        message_id = str(message.id)
                    except discord.Forbidden:
                        self.emit(
                            "error",
                            message=f"Missing permission to post the live notification for {sub['twitch_username']}.",
                        )
                        message_id = None
                    logs_cfg = self.data.logs.load()
                    if logs_cfg["events"].get("social_notifications", True):
                        self._log_event("social_notifications", f"Posted live notification for {sub['twitch_username']}")
                sub = {
                    **sub,
                    "is_live": True,
                    "last_stream_id": stream.get("id"),
                    "last_message_id": message_id,
                }
            elif not stream and was_live:
                # Stream just ended -- clean up the notification message
                # if the user has asked us to.
                if sub.get("delete_on_end") and channel and sub.get("last_message_id"):
                    try:
                        old_message = await channel.fetch_message(int(sub["last_message_id"]))
                        await old_message.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass
                    logs_cfg = self.data.logs.load()
                    if logs_cfg["events"].get("social_notifications", True):
                        self._log_event(
                            "social_notifications",
                            f"{sub['twitch_username']} went offline; deleted the live notification.",
                        )
                sub = {**sub, "is_live": False, "last_message_id": None}

            updated.append(sub)

        self.data.social_notifications.update(lambda d: {**d, "subscriptions": updated})

    @twitch_check_task.before_loop
    async def _before_twitch_check(self) -> None:
        await self.wait_until_ready()

    async def test_twitch_credentials(self) -> tuple:
        """Attempt to authenticate right now (instead of waiting for the
        next 2-minute cycle) so the UI can give immediate feedback."""
        social_cfg = self.data.social_notifications.load()
        client_id = social_cfg.get("twitch_client_id", "").strip()
        client_secret = social_cfg.get("twitch_client_secret", "").strip()
        if not client_id or not client_secret:
            return False, "Enter both a Twitch Client ID and Client Secret first."
        self._twitch_token = None  # force a fresh check, ignoring any cached token
        token = await self._get_twitch_token(client_id, client_secret)
        if token:
            return True, "Twitch credentials look valid."
        return False, "Twitch credentials were rejected by Twitch."

    # ------------------------------------------------------------------ #
    # Guild helpers
    # ------------------------------------------------------------------ #
    def _get_guild(self) -> Optional[discord.Guild]:
        if self.target_guild_id:
            guild = self.get_guild(self.target_guild_id)
            if guild:
                return guild
        # Fall back to first guild the bot is in.
        return self.guilds[0] if self.guilds else None

    async def _refresh_guild_snapshot(self) -> None:
        guild = self._get_guild()
        if not guild:
            self.emit("guild_info", found=False)
            return
        self.emit(
            "guild_info",
            found=True,
            name=guild.name,
            member_count=guild.member_count,
            channel_count=len(guild.channels),
            role_count=len(guild.roles),
        )

    async def fetch_roles(self) -> None:
        guild = self._get_guild()
        if not guild:
            self.emit("error", message="No connected server found to fetch roles from.")
            return
        roles = [
            {"id": str(r.id), "name": r.name, "color": r.color.value}
            for r in guild.roles
            if not r.is_default()
        ]
        self.data.roles.update(lambda d: {**d, "cached_roles": roles})
        self.emit("roles_fetched", roles=roles)

    async def fetch_channels(self) -> None:
        guild = self._get_guild()
        if not guild:
            self.emit("error", message="No connected server found to fetch channels from.")
            return
        channels = [
            {"id": str(c.id), "name": c.name}
            for c in guild.text_channels
        ]
        self.data.channels.update(lambda d: {**d, "cached_channels": channels})
        self.emit("channels_fetched", channels=channels)
        await self._refresh_guild_snapshot()

    async def refresh_all(self) -> None:
        await self.fetch_roles()
        await self.fetch_channels()

    # ------------------------------------------------------------------ #
    # Auto roles
    # ------------------------------------------------------------------ #
    async def on_member_join(self, member: discord.Member) -> None:
        roles_cfg = self.data.roles.load()
        role_ids = roles_cfg.get("auto_role_ids", [])
        if not role_ids:
            return
        roles_to_add = []
        for rid in role_ids:
            role = member.guild.get_role(int(rid))
            if role:
                roles_to_add.append(role)
        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason="SnapShield auto role")
                self._log_event("auto_roles", f"Assigned {len(roles_to_add)} role(s) to {member}")
            except discord.Forbidden:
                self.emit("error", message=f"Missing permission to assign auto roles to {member}")

        logs_cfg = self.data.logs.load()
        if logs_cfg["events"].get("joins", True):
            self._log_event("joins", f"{member} joined the server")

    async def on_member_remove(self, member: discord.Member) -> None:
        logs_cfg = self.data.logs.load()
        if logs_cfg["events"].get("leaves", True):
            self._log_event("leaves", f"{member} left the server")

    # ------------------------------------------------------------------ #
    # Reaction roles
    # ------------------------------------------------------------------ #
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.member is None or payload.member.bot:
            return
        panel = self._find_panel(payload.message_id)
        if not panel:
            return
        role_id = self._role_for_emoji(panel, payload.emoji)
        if not role_id:
            return
        guild = self.get_guild(payload.guild_id)
        if not guild:
            return
        role = guild.get_role(int(role_id))
        if role:
            try:
                await payload.member.add_roles(role, reason="SnapShield reaction role")
            except discord.Forbidden:
                self.emit("error", message="Missing permission to grant reaction role.")

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        panel = self._find_panel(payload.message_id)
        if not panel:
            return
        role_id = self._role_for_emoji(panel, payload.emoji)
        if not role_id:
            return
        guild = self.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        role = guild.get_role(int(role_id))
        if member and role:
            try:
                await member.remove_roles(role, reason="SnapShield reaction role removed")
            except discord.Forbidden:
                pass

    def _find_panel(self, message_id: int) -> Optional[dict]:
        panels = self.data.reaction_roles.load().get("panels", [])
        for panel in panels:
            if str(panel.get("message_id")) == str(message_id):
                return panel
        return None

    @staticmethod
    def _role_for_emoji(panel: dict, emoji: discord.PartialEmoji) -> Optional[str]:
        emoji_str = str(emoji)
        for mapping in panel.get("mappings", []):
            if mapping.get("emoji") == emoji_str or mapping.get("emoji") == emoji.name:
                return mapping.get("role_id")
        return None

    @staticmethod
    def _build_reaction_embed(embed_config: dict, mappings: list, guild: Optional[discord.Guild]) -> discord.Embed:
        """
        Build the embed shown for a reaction-role panel.

        Every visual field in `embed_config` is optional -- SnapShield only
        sets the ones the user actually filled in, so a bare-minimum panel
        (just emoji/role mappings, no title/description/etc.) still renders
        a clean, valid embed.
        """
        color = discord.Color.blurple()
        color_hex = (embed_config.get("color") or "").strip().lstrip("#")
        if color_hex:
            try:
                color = discord.Color(int(color_hex, 16))
            except ValueError:
                pass  # keep the default color if the hex is malformed

        embed = discord.Embed(
            title=embed_config.get("title") or None,
            description=embed_config.get("description") or None,
            color=color,
        )

        author_name = embed_config.get("author_name")
        if author_name:
            embed.set_author(name=author_name, icon_url=embed_config.get("author_icon_url") or None)

        thumbnail_url = embed_config.get("thumbnail_url")
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        image_url = embed_config.get("image_url")
        if image_url:
            embed.set_image(url=image_url)

        for mapping in mappings:
            role_name = mapping.get("role_id")
            if guild is not None:
                role = guild.get_role(int(mapping["role_id"]))
                if role:
                    role_name = role.name
            embed.add_field(name=mapping["emoji"], value=f"→ {role_name}", inline=False)

        footer_text = embed_config.get("footer") or "React with the emoji below to receive the matching role."
        embed.set_footer(text=footer_text)
        return embed

    async def send_reaction_panel(self, channel_id: int, embed_config: dict, mappings: list) -> Optional[dict]:
        """Send a new embedded reaction-role message and persist it. Returns panel dict or None."""
        channel = self.get_channel(channel_id)
        if channel is None:
            self.emit("error", message="Selected channel not found.")
            return None

        embed = self._build_reaction_embed(embed_config, mappings, channel.guild if hasattr(channel, "guild") else None)

        try:
            message = await channel.send(embed=embed)
            for mapping in mappings:
                try:
                    await message.add_reaction(mapping["emoji"])
                except discord.HTTPException:
                    # Invalid/unavailable emoji (e.g. a custom emoji the bot
                    # doesn't have access to) -- skip it but keep the panel.
                    self.emit("error", message=f"Could not react with {mapping['emoji']}; check the emoji is valid.")
        except discord.Forbidden:
            self.emit("error", message="Missing permission to post in that channel.")
            return None

        panel = {
            "id": str(message.id),
            "channel_id": str(channel_id),
            "message_id": str(message.id),
            "embed_config": embed_config,
            "mappings": mappings,
        }
        return panel

    async def delete_reaction_panel(self, panel: dict) -> bool:
        channel = self.get_channel(int(panel["channel_id"]))
        if channel is None:
            return False
        try:
            message = await channel.fetch_message(int(panel["message_id"]))
            await message.delete()
            return True
        except (discord.NotFound, discord.Forbidden):
            return False

    async def edit_reaction_panel(self, panel: dict, embed_config: dict) -> bool:
        channel = self.get_channel(int(panel["channel_id"]))
        if channel is None:
            return False
        try:
            message = await channel.fetch_message(int(panel["message_id"]))
            guild = channel.guild if hasattr(channel, "guild") else None
            embed = self._build_reaction_embed(embed_config, panel.get("mappings", []), guild)
            await message.edit(embed=embed)
            return True
        except (discord.NotFound, discord.Forbidden):
            return False

    # ------------------------------------------------------------------ #
    # Message moderation: word filters + strikes
    # ------------------------------------------------------------------ #
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return

        channels_cfg = self.data.channels.load()
        moderated_ids = set(channels_cfg.get("moderated_channel_ids", []))
        if moderated_ids and str(message.channel.id) not in moderated_ids:
            return  # channel not selected for moderation

        content_lower = message.content.lower()

        # Banned words -> instant punishment, no strike.
        banned_cfg = self.data.banned_words.load()
        for word in banned_cfg.get("words", []):
            if word and word.lower() in content_lower:
                await self._handle_banned_word(message, banned_cfg)
                return

        # Strike words -> add a strike.
        strike_words_cfg = self.data.strike_words.load()
        for word in strike_words_cfg.get("words", []):
            if word and word.lower() in content_lower:
                await self._handle_strike_word(message)
                return

    async def _handle_banned_word(self, message: discord.Message, banned_cfg: dict) -> None:
        channel = message.channel
        author_name = message.author.display_name
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await self._send_deletion_notice(channel, author_name)

        action = banned_cfg.get("action", "Kick")
        msg_text = banned_cfg.get("message", "You used prohibited language and have been removed.")
        member = message.author

        try:
            if msg_text:
                await member.send(msg_text)
        except discord.Forbidden:
            pass  # member has DMs disabled -- the channel notice still informs them

        try:
            if action == "Ban":
                await message.guild.ban(member, reason="SnapShield: banned word")
            else:
                await message.guild.kick(member, reason="SnapShield: banned word")
            self._log_event("bans" if action == "Ban" else "kicks", f"{member} {action.lower()}ned for banned word")
        except discord.Forbidden:
            self.emit("error", message=f"Missing permission to {action.lower()} {member}")

    async def _handle_strike_word(self, message: discord.Message) -> None:
        channel = message.channel
        author_name = message.author.display_name
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await self._send_deletion_notice(channel, author_name)

        member = message.author
        strikes_cfg = self.data.strikes.load()
        user_strikes = strikes_cfg.get("user_strikes", {})
        uid = str(member.id)
        count = user_strikes.get(uid, 0) + 1
        user_strikes[uid] = count
        self.data.strikes.update(lambda d: {**d, "user_strikes": {**d.get("user_strikes", {}), uid: count}})

        levels = strikes_cfg.get("levels", [])
        level_cfg = next((lv for lv in levels if int(lv.get("level", 0)) == count), None)
        if level_cfg is None and levels:
            # If the user's strike count exceeds the highest configured
            # level, re-apply the harshest configured action.
            level_cfg = max(levels, key=lambda lv: int(lv.get("level", 0)))

        self._log_event("strikes", f"{member} received strike #{count}")

        if level_cfg is None:
            return

        action = level_cfg.get("action", "Warning")
        msg_text = level_cfg.get("message", "")

        try:
            if msg_text:
                await member.send(msg_text)
        except discord.Forbidden:
            pass

        try:
            if action == "Warning":
                pass  # message already sent (or channel notice below)
            elif action == "Timeout":
                minutes = int(level_cfg.get("duration_minutes", 60))
                until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
                await member.timeout(until, reason=f"SnapShield strike {count}")
                self._log_event("timeouts", f"{member} timed out ({minutes} min) at strike #{count}")
            elif action == "Kick":
                await message.guild.kick(member, reason=f"SnapShield strike {count}")
                self._log_event("kicks", f"{member} kicked at strike #{count}")
            elif action == "Ban":
                await message.guild.ban(member, reason=f"SnapShield strike {count}")
                self._log_event("bans", f"{member} banned at strike #{count}")
        except discord.Forbidden:
            self.emit("error", message=f"Missing permission to apply '{action}' to {member}")

    async def on_message_delete(self, message: discord.Message) -> None:
        logs_cfg = self.data.logs.load()
        if logs_cfg["events"].get("deleted_messages", True) and message.guild is not None:
            author = getattr(message, "author", "Unknown")
            self._log_event("deleted_messages", f"Message by {author} deleted in #{message.channel}")

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content == after.content or before.guild is None:
            return
        logs_cfg = self.data.logs.load()
        if logs_cfg["events"].get("edited_messages", True):
            self._log_event("edited_messages", f"{before.author} edited a message in #{before.channel}")

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    def _log_event(self, category: str, text: str) -> None:
        """Record an event both to the local dashboard log and Discord log channel."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"time": timestamp, "category": category, "text": text}

        def _append(d):
            history = d.get("history", [])
            history.append(entry)
            d["history"] = history[-200:]  # keep the log file bounded
            return d

        self.data.logs.update(_append)
        self.emit("log_event", entry=entry)

        logs_cfg = self.data.logs.load()
        channel_id = logs_cfg.get("log_channel_id") or self.data.channels.load().get("log_channel_id")
        if channel_id and self.is_ready():
            channel = self.get_channel(int(channel_id))
            if channel:
                self.loop.create_task(self._safe_send(channel, f"**[{category}]** {text}"))

    @staticmethod
    async def _safe_send(channel, text: str) -> None:
        try:
            await channel.send(text)
        except discord.Forbidden:
            pass

    @staticmethod
    async def _send_deletion_notice(channel, username: str) -> None:
        """Post the required in-channel notice whenever a moderated
        message is removed, pointing the member to their DMs."""
        try:
            await channel.send(f"Message deleted — {username}, check your DMs.")
        except discord.Forbidden:
            pass
