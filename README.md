# SnapShield

A locally-hosted Discord moderation bot with a native Windows desktop
interface, built with **Python 3.12+**, **discord.py**, and **PyQt6**.
All configuration is stored in plain JSON files under `data/` — no
database required.

## Features

- **Bot Settings** — connect/disconnect with a masked, validated token field
- **Auto Roles** — assign one or more roles automatically on member join
- **Reaction Roles** — build and manage self-assign reaction-role panels
- **Moderation** — pick exactly which channels are monitored
- **Strike System** — unlimited, fully configurable escalation levels
  (Warning / Timeout / Kick / Ban)
- **Word Filters** — separate Strike Words and Banned Words lists, with
  import/export
- **Logging** — route moderation events to a Discord channel, with
  per-category toggles
- **Server Sync** — refresh roles/channels live, no restart needed
- **Social Notifications** — track Twitch channels and post a rich
  "went live" embed (thumbnail, game, viewer count) in a Discord
  channel of your choice, with an optional role ping and an option to
  auto-delete the notification once the stream ends
- **Dashboard** — live bot status, server info, and configuration counts
- **Keep-alive handshake** — a background task refreshes presence every
  5 minutes and discord.py's gateway auto-reconnects/resumes on drops
- **Automatic strike reset** — all user strike counts are cleared every
  12 hours
- Deleting a moderated message posts a channel notice pointing the
  member to their DMs, and reaction-role panels are sent as embeds
  listing every emoji → role pairing

## Project layout

```
SnapShield/
├── main.py              # entry point
├── ui/
│   ├── main_window.py    # sidebar + page routing
│   ├── theme.py           # dark theme stylesheet
│   ├── widgets.py         # shared Card/Toast/page-header widgets
│   └── pages/              # one module per sidebar page
├── bot/
│   ├── discord_bot.py     # discord.py client + moderation logic
│   └── bot_thread.py      # QThread bridging asyncio <-> Qt
├── storage/
│   └── json_store.py      # JSON persistence (auto-creates data/*.json)
├── data/                  # created automatically at first run
├── assets/                # icons, etc. (optional)
├── logs/                  # rotating snapshield.log
├── requirements.txt
└── SnapShield.spec        # PyInstaller build spec
```

## Setup (development)

1. Install Python 3.12 or newer.
2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python main.py
   ```

4. In the **Bot Settings** page, paste in the bot token, client ID, and
   guild ID from the [Discord Developer Portal](https://discord.com/developers/applications),
   then click **Connect Bot**.

   Your bot needs these **Privileged Gateway Intents** enabled in the
   Developer Portal: `SERVER MEMBERS INTENT` and `MESSAGE CONTENT INTENT`.

5. For **Social Notifications**, register a free app at the
   [Twitch Developer Console](https://dev.twitch.tv/console/apps) (any
   OAuth Redirect URL works, e.g. `http://localhost`), then paste its
   Client ID and Client Secret into the Social Notifications page and
   click **Test Connection**. SnapShield only uses these to make
   read-only "is this channel live" API calls via the client-credentials
   flow -- no user login or Twitch account access is required.

## Building the Windows executable

With the virtual environment active:

```bash
pyinstaller --onefile --windowed --name SnapShield main.py
```

or, using the included spec file (recommended — it also bundles the
`assets/` folder and declares the hidden imports discord.py/PyQt6 need):

```bash
pyinstaller SnapShield.spec
```

The finished executable is written to `dist/SnapShield.exe`. The first
time it runs it will create a `data/` folder and a `logs/` folder next
to the executable.

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
| `reaction_roles.json`  | Reaction-role panel definitions             |
| `logs.json`            | Log channel, event toggles, recent history  |
| `social_notifications.json` | Twitch API credentials, tracked channels |

## Security notes

- The bot token field is masked by default (toggle with **Show/Hide**).
- Token format is sanity-checked client-side before an actual Discord
  login is attempted; real validation happens against Discord itself
  when you click **Connect Bot**.
- Corrupted JSON files are automatically backed up (`*.corrupt.bak`)
  and reset to safe defaults instead of crashing the app.
- Keep your `data/settings.json` private — anyone with your bot token
  can control your bot. Never commit it to a public repository.
