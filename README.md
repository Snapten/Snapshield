# SnapShield

A locally-hosted **Twitch** bot suite with a native Windows desktop
interface, built with **Python 3.12+**, **PyQt6**, and **aiohttp**. A
Discord login lets it send clips and alerts to your Discord channels.
All configuration is stored in plain JSON files under `data/`.

> Discord server moderation is now handled by the web dashboard; the
> desktop app is Twitch-only.

## Twitch Features

Alerts, Commands, and Channel Points all build what happens using the
same **action chain** editor — an ordered list of steps that fire in
sequence, each its own collapsible card with a header row (test just
this step, move up/down, duplicate, help, delete, collapse) and its
fields shown inline. The available step types are the same everywhere:

- **Chat Message** — send a message to Twitch chat
- **Overlay** — show an image or video (uploaded file, or the
  triggering user's live avatar) on a chosen overlay — position, size,
  and separate in/out effects
- **Text** — styled text on a chosen overlay — its own font, size,
  color, bold, position, and in/out effects
- **Sound** — play a sound through a chosen overlay, at a volume you set
- **Command** — run one of your existing chat commands
- **Discord** — post a message to a channel in your Discord server
  (log in on the Discord page first)
- **Moderation** — apply Give Strike / Timeout / Ban to whoever
  triggered the chain (the redeemer, follower, raider, subscriber, or
  command user/target). Twitch has no "kick" or custom roles the way
  Discord does, so those aren't options here
- **Wait** — a pure pause before the next step

Every step has its own delay (seconds before it fires, relative to the
chain starting), so steps can be staggered rather than firing all at
once.

- **Accounts** — log in with your **Streamer account** (required) and,
  optionally, a separate **Bot account**. Both use Twitch's device-code
  flow (a short code shown in-app, entered at twitch.tv/activate — no
  browser popups or local redirect server). Account precedence: if a
  Bot account is logged in, chat and moderation actions (messages,
  timeouts, bans) are performed as the bot; if not, they're performed
  as the streamer account directly, so a single account is enough to
  run everything.
- **Alerts** — a generic builder covering every event SnapShield reacts
  to: Follow, Raid, Subscription, Gift Sub, and Mass Gift Sub. Pick the
  event, write the chat message using that event's token placeholders
  (e.g. `{user}`, `{viewers}`, `{tier}`, `{count}`), and toggle it on
  or off. Mass Gift Sub has a settable minimum-gift-count threshold —
  a community gift batch below that size falls back to a regular Gift
  Sub shout-out instead of staying silent. Follows, raids, subscriptions, and gift subscriptions are handled
  through Twitch EventSub so they can recover cleanly when OAuth tokens
  rotate. Each alert can also trigger an **overlay**: an image, video,
  or that event's live Twitch avatar (positioned and sized in pixels),
  a sound, and/or on-screen text with its own font/size/color — plus
  an entrance/exit animation (fade, or slide in from and out toward a
  direction). "Duplicate Selected" clones an alert as a starting
  template for a new one.
- **Overlay** — SnapShield hosts browser-source overlays locally for
  OBS. A "Default" overlay is created automatically; copy its address
  with one click and add it as an OBS Browser Source (1920×1080
  recommended). Add more overlays for different placements. A manual
  "Send to Overlay" form lets you push an image, video, sound, and/or
  styled text immediately — handy for testing an alert's setup, or
  just using the overlay standalone for music, image displays, or
  video clips independent of any alert. Media only starts playing the
  moment it's actually sent (a fresh copy is always fetched, so a
  GIF/video never resumes mid-loop from a previous trigger).
- **Twitch Moderation** — the same model as Discord: an unlimited,
  configurable strike ladder (Warning / Timeout / Ban) plus a separate
  instant-action Banned Words list, both with import/export.
- **Commands** — custom chat commands with a name, a minimum
  permission level (Everyone / Subscriber / VIP / Moderator /
  Broadcaster), a response, and an on/off toggle. Commands support the
  same overlay media/sound/text/animation options as Alerts, including
  a dynamic "avatar" media type — e.g. `!shoutout somename` can show
  that user's live Twitch profile picture on screen automatically.
  Ships pre-seeded with common commands other bots use: `!discord`,
  `!socials`, `!lurk`, `!uptime`, `!followage`, `!shoutout`,
  `!commands` — the last four are "smart" built-ins the bot fills in
  dynamically via the Twitch API, but their response templates,
  permissions, and overlay media are still fully editable.
  "Duplicate Selected" clones a command (including a built-in) as a
  regular, independently-editable copy under a new name.
- **Games** — Twitch-only mini games backed by a single
  `data/gamedata.json` file. Includes configurable **Slots**, **Coin
  Flip**, **High/Low Dice**, **8 Ball**, `!balance`, and `!daily`.
  Configure starting coins, default/max bets, daily rewards, per-game
  toggles, and cooldowns. Player balances and simple win/loss stats stay
  in `gamedata.json` rather than being added to the other data files.
- **Channel Points** — attach the same kind of action chain (chat
  message, sound, overlay image/video/text, delay, Discord post) to
  one of your existing Channel Points custom rewards. "Fetch Rewards"
  pulls in your channel's rewards; SnapShield attaches chains to
  rewards you've already created rather than creating new ones itself,
  since reward creation via the API requires Affiliate/Partner status
  and most streamers already have their rewards set up how they want.
  Tokens: `{user}`, `{reward_title}`, `{cost}`, `{user_input}` (the
  viewer's typed message, if the reward asks for one). Redemptions are
  detected in real time via EventSub — this is the one part of
  SnapShield's Twitch integration that genuinely requires it, since
  Twitch restricts the alternative (polling the redemptions list, and
  marking a redemption fulfilled) to only the app that originally
  created the reward. That restriction also means the automatic
  "mark as fulfilled" step will typically fail quietly for a
  dashboard-created reward — that's expected, and doesn't affect
  whether the action chain fires.

**Important:** if you log in a separate Bot account, it must actually
be modded in your channel (type `/mod <botaccountname>` in your own
Twitch chat) before its timeouts/bans/message-deletion will work —
Twitch's moderation API requires the acting account to hold moderator
status on the channel, same as any other Twitch bot.

**Note:** the overlay web server starts automatically with the app on
`http://127.0.0.1:5757` and runs the whole time SnapShield is open,
independent of whether the Discord or Twitch bot is connected — so
you can set up and test overlays any time. If port 5757 is already in
use on your machine, edit `host`/`port` directly in
`data/twitch_overlays.json` (there's no in-app setting for this yet).



```
SnapShield/
├── main.py              # entry point
├── ui/
│   ├── main_window.py    # sidebar + page routing
│   ├── theme.py           # dark theme stylesheet
│   ├── widgets.py         # shared Card/Toast/page-header widgets
│   └── pages/              # one module per sidebar page
├── bot/
│   ├── discord_login.py   # Discord OAuth login + webhook posting
│   ├── twitch_auth.py     # Twitch device-code OAuth flow
│   ├── twitch_auth_manager.py # shared OAuth validation/refresh coordinator
│   ├── twitch_login_thread.py  # one-shot QThread for a single account login
│   ├── twitch_bot.py      # Twitch IRC chat, moderation, commands, games, follows
│   ├── twitch_thread.py   # QThread bridging Twitch asyncio <-> Qt
│   ├── overlay_server.py  # local aiohttp web/WebSocket server for OBS overlays
│   └── overlay_thread.py  # QThread hosting the overlay server
├── storage/
│   └── json_store.py      # JSON persistence (auto-creates data/*.json)
├── data/                  # created automatically at first run
├── assets/                # icons, etc. (optional)
├── logs/                  # rotating snapshield.log
├── requirements.txt
└── SnapShield.spec        # PyInstaller build spec
```

## Setup — Twitch Bot mode

1. The **Twitch Client ID is bundled with SnapShield**. You do not need
   to enter a Client ID or Client Secret. SnapShield uses the public
   Device Code Grant for Windows desktop authentication.
2. Click **Log in with Streamer Account**, then follow the on-screen
   code to twitch.tv/activate. This account is required — SnapShield
   uses it to know which channel to join, and it requests enough
   scope to run chat/moderation/follows entirely on its own.
3. Optionally, click **Log in with Bot Account** using a *second*
   Twitch account. If you do this, remember to `/mod` that account in
   your own channel afterward, or its moderation actions will be
   rejected by Twitch's API.
4. Click **Connect Twitch Bot**. Configure the strike ladder, banned
   words, and commands on their respective pages — changes take
   effect immediately, no reconnect needed.

## Special identifiers (tokens)

Alert messages, command responses, and overlay text can all include
placeholders in `{curly_braces}` — SnapShield fills them in with real
values when the message actually fires. Which tokens are available
depends on what triggered the message:

**Alerts** (shown as a hint under the Message field once you pick an
event on the Alerts page):

| Event | Available tokens |
|---|---|
| Follow | `{user}` |
| Raid | `{user}` (the raider), `{viewers}` (raid size) |
| Subscription | `{user}`, `{tier}` (Tier 1/2/3 or Prime), `{months}` |
| Gift Sub | `{user}` (the gifter), `{recipient}` |
| Mass Gift Sub | `{user}` (the gifter), `{count}` (subs gifted) |

**Commands**: every command gets `{user}` (whoever ran it) and
`{channel}`. A few built-in commands add their own:

| Command | Extra tokens |
|---|---|
| `!uptime` | `{uptime}` |
| `!followage` | `{followage}` |
| `!shoutout <name>` | `{target}` (display name), `{target_game}` |
| `!commands` | `{commands_list}` |

Any command — built-in or custom — that includes `{target}` or
`{target_game}` in its text, or uses an overlay image/video with its
Media Source set to "Avatar," automatically resolves that target the
same way `!shoutout` does: the first argument's user if one was
given (e.g. `!hug somename`), otherwise whoever ran the command.

Renaming a built-in command (e.g. renaming `!uptime` to `!howlong`)
turns it into a plain command and drops its special dynamic token —
it'll only have `{user}`/`{channel}` from then on.

**Channel Points**: `{user}` (the redeemer), `{reward_title}`,
`{cost}`, `{user_input}` (the viewer's typed message, if the reward
asks for one — blank otherwise).

## Running from source

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

## Setup — Discord login (clips and alerts)

SnapShield no longer runs a Discord bot (Discord moderation now lives on
the web dashboard). Instead the desktop app logs in with Discord so it can
post Twitch clips, alerts, bridge messages and stream summaries to your
channels.

1. Create an application at the [Discord Developer Portal](https://discord.com/developers/applications).
2. **OAuth2 → Redirects**: add `http://127.0.0.1:17343/callback`.
3. Put the application's Client ID and Client Secret in `config/discord.py`
   (or set `SNAPSHIELD_DISCORD_CLIENT_ID` / `SNAPSHIELD_DISCORD_CLIENT_SECRET`).
4. In SnapShield open **Discord → Log in with Discord / Add channel**. Discord
   asks which server and channel to allow (scope `webhook.incoming`); run the
   login again to add more channels. No bot token is needed.
5. Optional: tick **Post every clip created by SnapShield to Discord** and pick
   a channel and message (`{username}`, `{clipTitle}`, `{clipUrl}`).

The Discord action step, the Twitch → Discord page and Stream Analytics
summaries all pick from the channels authorised here.

## Building the Windows executable

With the virtual environment active:

```bash
pyinstaller --onefile --windowed --name SnapShield main.py
```

or, using the included spec file (recommended — it also bundles the
`assets/` folder, which the plain command above does not, so the
sidebar logo and window icon are only present when built this way):

```bash
pyinstaller SnapShield.spec
```

The finished executable is written to `dist/SnapShield.exe`. When run as an exe, SnapShield saves its settings (`data/`) and logs (`logs/`) in `%APPDATA%\SnapShield`, not next to the program. Create an empty file named `portable.txt` beside `SnapShield.exe` to keep them next to the exe instead.

> **Note:** `SnapShield.spec` relies on PyInstaller's own bundled hooks
> for aiohttp and PyQt6 to find their hidden imports rather
> than declaring them explicitly. If a real Windows build ever fails
> with a `ModuleNotFoundError` for something that clearly is installed,
> add it to the `hiddenimports=[]` list in the spec.

Before building a release, bump the version so it doesn't stay stale
across builds — this is the one thing that has to be remembered:

```bash
python bump_version.py          # 0.45.1 -> 0.45.2
python bump_version.py minor    # 0.45.1 -> 0.46.0
python bump_version.py 0.50.0   # set an exact version
```

This is the only place the version lives (`config/version.py`) — the
sidebar footer, the Diagnostics update-check display, and
`updater_service.py`'s update comparisons all read from it already.

> **Note:** PyInstaller builds a Windows `.exe` only when run **on
> Windows** (it does not cross-compile). Run the build command above
> from a Windows machine or a Windows CI runner.

## Data files

All configuration lives under `data/` as JSON, and is created
automatically the first time it's needed:

| File                  | Contents                                   |
|-----------------------|---------------------------------------------|
| `settings.json`        | Bot token, client ID, guild ID              |
| `roles.json`           | Cached Discord roles, auto-role selections  |
| `channels.json`        | Cached channels, moderated-channel list     |
| `strikes.json`         | Strike level ladder, per-user strike counts |
| `strike_words.json`    | Strike-word list                            |
| `banned_words.json`    | Banned-word list, action, custom message    |
| `spam_detector.json`   | Cross-channel spam detector settings        |
| `reaction_roles.json`  | Reaction-role panel definitions             |
| `logs.json`            | Log channel, event toggles, recent history  |
| `social_notifications.json` | Twitch API credentials, tracked channels |
| `twitch_accounts.json` | Twitch streamer/bot account tokens, follower-announce settings |
| `twitch_alerts.json` | Follow/raid/sub/gift-sub alert messages and toggles |
| `twitch_moderation.json` | Twitch strike ladder, banned/strike words |
| `twitch_commands.json` | Custom Twitch chat commands |
| `gamedata.json` | Twitch mini-game settings, balances, and player stats |
| `channel_points.json` | Channel Points reward action chains |
| `twitch_overlays.json` | Registered overlays, local server host/port |
| `overlay_media/` (folder) | Uploaded images/videos/sounds used by alerts and manual overlay sends |

## Security notes

- Discord login uses OAuth (`webhook.incoming`); the resulting channel webhook URLs are stored in plain text in `data/discord_connection.json`. Keep the `data/` folder private.


## Twitch !clip workflow

The built-in `!clip` command now runs an action chain: it replies in Twitch chat, creates a Twitch clip, waits for Twitch to confirm the clip exists, then posts the finished clip URL to a selected Discord channel. The clip step exposes `{username}`, `{clipUrl}`, `{clipTitle}`, and `{clipId}` to following actions. Twitch clip creation requires the streamer's OAuth token to include `clips:edit`; re-login the Streamer account after upgrading to grant that scope.


## v0.25 UI and Twitch connection updates

- Discord sidebar now groups Strike System, Word Filters, Spam Detector, and moderation channel controls under one **Moderation** tabbed section.
- Removed the redundant manual **Send to Overlay** panel; overlays remain managed from the overlay list and are driven by action chains.
- **Server Sync** includes an optional full refresh on application startup.
- Added **Twitch > Sponsor Banner**. It uses the shared action-chain editor, starts when the stream is detected live, repeats at the configured minute interval, and stops when the stream is offline.
- Twitch startup now validates persisted OAuth tokens and refreshes them when possible.
- A periodic Twitch handshake keeps the API session healthy and forces IRC reconnects when the active token needs attention.

### Twitch application ID
The SnapShield Twitch Client ID is bundled in `config/twitch.py`; users do not need to enter it. The Twitch Client Secret is never shipped with the application.

### v0.33 Twitch OAuth reliability
- Twitch OAuth validation uses Twitch's `/oauth2/validate` endpoint rather than treating a Helix `/users` request as the OAuth health check.
- Streamer and optional Bot refreshes are coordinated through `bot/twitch_auth_manager.py`, which serializes rotating public-client refresh-token use across the Twitch and Discord worker threads.
- Access tokens are proactively refreshed shortly before their known expiry and reactively refreshed after an explicit Twitch authentication rejection.
- A successful OAuth refresh deliberately reconnects IRC with the new access token and rebuilds the Twitch EventSub connection when the Streamer token changes.
- Twitch chat is not reported as connected until IRC returns numeric `001`; `NOTICE :Login authentication failed` is treated as an authentication failure and triggers recovery.
- Diagnostics now reports Twitch IRC authentication and saved OAuth health, including token expiry/refresh information.
- Public Device Code refresh tokens can still eventually require interactive reauthorization if Twitch expires or revokes the saved refresh authorization; SnapShield surfaces this as **Reauthorization required** instead of silently claiming the bot is online.


## Windows release and updates

SnapShield ships as two Windows executables that must sit **side by side**:

- `SnapShield.exe` — the main desktop application.
- `SnapShieldUpdater.exe` — a small helper that swaps in the new EXE after SnapShield exits.

The **installer** (Inno Setup 6, `installer/SnapShield.iss`) installs both per-user into `%LOCALAPPDATA%\Programs\SnapShield` with no administrator prompt. That matters: the updater replaces `SnapShield.exe` itself, which only works when the install folder is writable without admin rights. User data lives separately in `%APPDATA%\SnapShield` (`data\`, `logs\`, `updates\`), so installs, upgrades and updates never touch it. Uninstalling keeps it unless the user ticks "also delete settings".

### Publishing a release (your steps)

1. `python bump_version.py minor` (or `patch` / `major`) — every build needs a new version.
2. `python build_release.py` (on Windows, with `pip install -r requirements.txt`). It writes to `release/`:
   - `SnapShield-<version>.zip` — the **update** package (just `SnapShield.exe`).
   - `SnapShield-Setup-<version>.exe` — the **installer** for the website button (built automatically if Inno Setup 6 is installed; otherwise the script prints the `ISCC.exe` command to run).
   - `SnapShield-Full-<version>.zip` — optional portable download (both EXEs + a short README).
   - `update-manifest.json` — version, download URL, SHA-256 and notes.
3. Upload `SnapShield-<version>.zip` to `UPDATE_DOWNLOAD_BASE` (`https://github.com/Snapten/Snapshield/releases/download/twitch/`, the GitHub release tagged `twitch`), and `SnapShield-Setup-<version>.exe` as the website download.
4. Edit `notes` in `update-manifest.json`, then upload it to `UPDATE_MANIFEST_URL` (`https://snapshield.snapten.uk/update-manifest.json`) **last**, so nobody is offered an update whose file isn't live yet.

### What users see

- A few seconds after launch SnapShield quietly checks the manifest. If a newer version exists it asks "Version X is available. Update now or later?" (and notes if the Twitch bot is connected). **Update now** downloads, verifies and restarts; **Later** just keeps going, and the sidebar footer keeps showing **Update available** until they update.
- **Diagnostics → Check for Updates → Download & Install Update** downloads the ZIP, verifies its SHA-256, closes SnapShield, swaps the EXE and restarts it.
- Their settings and logs (in `%APPDATA%\SnapShield`) are never touched. The updater keeps a backup of the old EXE and restores it if anything fails, and writes `updater.log` to the logs folder.
- URLs live in `config/update.py`. Both the manifest and the ZIP must be served over HTTPS.

### Music account login
- Spotify and YouTube Music no longer ask end users to paste access tokens.
- The Music page opens the provider's normal browser login and returns to SnapShield through a temporary localhost OAuth callback.
- OAuth access/refresh tokens are stored locally in `data/music_accounts.json` and are never shown in the UI.
- The SnapShield developer must bundle the provider OAuth Client IDs in `config/music.py` (or provide them through `SNAPSHIELD_SPOTIFY_CLIENT_ID` and `SNAPSHIELD_GOOGLE_CLIENT_ID`). End users should not create or paste provider developer credentials.
- YouTube also needs a bundled Client Secret (`SNAPSHIELD_GOOGLE_CLIENT_SECRET` or `GOOGLE_CLIENT_SECRET` in `config/music.py`) — Google's token endpoint requires one for "Desktop app" OAuth clients even with PKCE, unlike Spotify. This secret isn't confidential in an installed app; it's still fine to bundle it the same way as the Client ID.

### Song requests (Spotify / YouTube)
- Configured per-provider on the Music page: an enable checkbox, a chat trigger command (default `!songrequest`), a minimum permission level, a cooldown, and an Action Chain that runs on a successful request with `{track}` `{artist}` `{album}` `{duration}` `{url}` `{requested_by}` tokens available (plus the usual `{user}`/`{username}`/`{channel}`). An empty Action Chain still confirms the request with a plain chat message.
- **Spotify**: searches for the requested track and adds it to the connected account's playback queue. This requires the connected Spotify account to have **Spotify Premium** (free accounts can't be playback-controlled via the API) and an active Spotify device open somewhere (desktop app, mobile app, or the web player at open.spotify.com all count).
- **YouTube**: the official YouTube Data API has no live playback-queue endpoint, so a request instead adds the found video to a playlist you configure (paste the target playlist's ID on the Music page — the ID is the `list=` value in that playlist's URL). The playlist must already exist and be owned by the connected account.
- YouTube song requests need the broader `https://www.googleapis.com/auth/youtube` scope (not just `.readonly`) to write to a playlist. Anyone who connected YouTube before this feature was added needs to **Disconnect and Connect YouTube again** on the Music page to re-consent to the new scope — an old token won't have it and playlist adds will fail with a 403 until then.
- Access tokens are refreshed automatically (Spotify via its public-client PKCE refresh, YouTube via the bundled Client Secret) whenever a song request is made and the stored token is expired or close to it.
- If both providers are enabled with the same trigger command, Spotify takes priority and YouTube's copy of that command is effectively unreachable — give each provider its own command if you enable both.

### Now Playing, Queue, Skip, and auto-announce
- Configured on the Music page's "Now Playing" tab, separate from song requests since these apply regardless of whether song requests are even enabled.
- **Now Playing command** (`!song` by default, aliases configurable) shows whichever source is active: Spotify if connected and actively playing, otherwise whatever the Basic Player last loaded. Enabled by default.
- **Queue command** (`!queue` by default) shows the next 3 upcoming Spotify tracks, falling back to the Basic Player's next few tracks when Spotify isn't connected (only predictable when Shuffle is off). Enabled by default.
- **Skip command** (`!skipsong` by default, moderator-only by default) skips the currently playing Spotify track, falling back to advancing the Basic Player when Spotify isn't connected (acts within ~1.5s, since the bot thread can't call into the UI's media player directly). Disabled by default since it's a destructive action — enable it explicitly once you're comfortable with who can use it.
- **Playback device selection**: the Spotify tab has a "Playback device" picker (Refresh Devices, then choose one) used by song requests and Skip, for when more than one Spotify Connect device is open and requests keep landing on the wrong one. Leaving it on "Whatever's currently active" preserves the original behavior. The Basic Player tab has its own, unrelated "Playback device" picker for local audio output (which sound card/speakers the local player uses) — YouTube has no such setting since its API doesn't control playback on any device.
- **Auto-announce** polls Spotify every N seconds (configurable, minimum 10s to be considerate of rate limits) and fires an Action Chain in chat whenever the playing track changes, with `{track}` `{artist}` `{album}` `{duration}` `{url}` tokens. Disabled by default. An empty Action Chain still posts a plain "🎵 Now playing: ..." message.
- All of the above that touch Spotify need the same Premium + active-device conditions as song requests.
- **Basic Player integration**: Now Playing, Queue, and Skip all fall back to the Basic Player when Spotify isn't connected. Now Playing shows the last-loaded local track; Queue shows the next few tracks in play order (only when Shuffle is off, since shuffle order can't be predicted ahead of time); Skip flags a request the Basic Player tab picks up and acts on within ~1.5s (the bot thread can't call into the UI's media player directly).
- **Basic Player's own Action Chain** (on the Basic Player tab itself) now actually runs — it fires every time a local track starts, including a repeated/looped track, with `{track}` `{artist}` `{album}` `{duration}` `{folder}` tokens read from the file's own tags (via Qt's built-in media metadata, so no extra dependency). Untagged files (e.g. most `.wav`) fall back to the filename for `{track}` with the other fields empty, and the announce waits up to ~1.5s for tags to load before firing. Upcoming tracks shown by `!queue` are filenames only, since tags can only be read from the file currently loaded in the player. This is separate from the Now Playing tab's Spotify auto-announce and has its own enable toggle and Save button.
- Spotify's callback listens on a **fixed** local port (`SPOTIFY_REDIRECT_PORT` in `config/music.py`, default `17342`, overridable with `SNAPSHIELD_SPOTIFY_REDIRECT_PORT`). That exact `http://127.0.0.1:<port>/callback` must be registered as a Redirect URI on the Spotify app, since some Spotify developer dashboards reject a port-less loopback URI even though Spotify's docs describe it as supported.
- YouTube's callback uses a dynamically assigned port each login, since Google's "Desktop app" OAuth client type accepts any loopback port without pre-registration.


## v0.50.0 — Twitch-only app with Discord login
- Removed the Discord bot suite from the desktop app (Dashboard, Bot Settings, Community, Moderation, Commands, Economy, Voice, Webhooks, Logging, Social Notifications) and the Discord/Twitch mode switch. `discord.py` is no longer required.
- New **Discord** page: log in with Discord and authorise channels for posting (see *Setup — Discord login*).
- New automatic clip posting with an embed; the Discord action step, Twitch → Discord bridge and analytics summaries use the authorised channels. Discord → Twitch chat relay was removed (it needed the bot).

## v0.50.2 — no more 4-hourly Twitch disconnects
- Twitch access tokens last about 4 hours. When SnapShield refreshed one, it used to deliberately close the chat (IRC) and EventSub connections to "rotate" them, which caused a disconnect and missed chat/alerts every ~4 hours. Refreshes now happen silently and live connections stay up; any genuine reconnect still picks up the fresh token.

## v0.50.3 — updater ready for release
- Update feed configured for snapshield.snapten.uk; startup update check with a sidebar "Update available" notice.
- Updater retries while Windows still locks the old EXE, keeps a backup it restores on failure, logs to `logs/updater.log`, and relaunches SnapShield with a clean environment (avoids the PyInstaller "Failed to load Python DLL" relaunch bug).
- `build_release.py` now also builds the first-install ZIP (both EXEs) and writes the real download URL into the manifest. UPX compression is off to reduce antivirus false positives.

## v0.50.5 — settings now saved beside the exe
- Fixed settings not persisting in the built .exe: the data folder was being resolved relative to the module's __file__, which in a PyInstaller one-file build is a temporary folder deleted on exit. `data/` now lives beside SnapShield.exe (same place as `logs/`).

## v0.50.6 — data and logs in AppData, Inno Setup installer
- The exe now keeps `data/`, `logs/` and `updates/` in `%APPDATA%\SnapShield` (override with a `portable.txt` beside the exe, or the `SNAPSHIELD_DATA_DIR` environment variable), so the program can be installed anywhere and nothing is written next to it.
- Added `installer/SnapShield.iss` (Inno Setup 6, per-user install, optional settings removal on uninstall) and hooked it into `build_release.py`.

## v0.50.8 - overlays back on localhost

- The overlay server listens on `127.0.0.1` only and the Overlay page shows `http://127.0.0.1:5757/overlay/<id>` (OBS must run on the same PC). Older saved host values are ignored.

## v0.50.7 - update prompt on startup
- The startup update check now asks "Version X is available. Update now or later?". Update now jumps to Diagnostics, shows download progress and installs without a second confirmation; Later never interrupts again that session. It never restarts the app on its own, so a live stream isn't interrupted unexpectedly.
