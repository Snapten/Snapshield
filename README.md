# 🛡️ SnapShield

<p align="center">

A powerful desktop Twitch automation suite with overlays, alerts, moderation,
channel points, Discord integration, music tools, mini-games and more.

Built with Python, PyQt6 and Twitch EventSub.

</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-377for-the-badge&logo=python&logoColor=white
  <img src="https://img.shields.io/badge/PyQt6-GUI-41=for-the-badge
  <img src="https://img.shields.io/badge/Twitch-EventSub-9146FF?style=for-the-badge&logo=twitch&logoColorimg src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white">
# ✨ What is SnapShield?

SnapShield is a locally-hosted Twitch automation platform designed for streamers who want powerful tools without relying on cloud services or monthly subscriptions.

Everything runs on your own PC.

✅ Twitch Alerts

✅ OBS Overlays

✅ Channel Point Automations

✅ Chat Commands

✅ Twitch Moderation

✅ Discord Posting

✅ Clip Creation

✅ Music Integration

✅ Mini Games

✅ Automatic Updates

---

## 🚀 Why SnapShield?

Unlike traditional Twitch bots, SnapShield combines multiple streaming tools into a single desktop application.

| Feature | SnapShield |
|----------|------------|
| Native Windows Application | ✅ |
| No Monthly Subscription | ✅ |
| Local OBS Overlays | ✅ |
| EventSub Support | ✅ |
| Built-in Mini Games | ✅ |
| Discord Integration | ✅ |
| Automatic Updates | ✅ |
| Fully Custom Action Chains | ✅ |

---

# 🎬 Core Features

## ⚙️ Action Chains

The heart of SnapShield.

Alerts, commands, sponsor banners and channel point rewards all use the same Action Chain system.

Build workflows visually by combining:

| Action | Description |
|----------|-------------|
| 💬 Chat Message | Send Twitch messages |
| 🖼️ Overlay Media | Images, videos or avatars |
| 📝 Text Overlay | Styled text with animations |
| 🔊 Sound | Play audio effects |
| 🎮 Command | Trigger another command |
| 🌐 Discord | Send Discord messages |
| 🛡️ Moderation | Warn, timeout or ban |
| ⏳ Wait | Pause before next action |

Each action can have its own timing, allowing complex automated sequences.

---

## 📢 Twitch Alerts

Create custom automated reactions for:

- Follows
- Raids
- Subscriptions
- Gift Subs
- Mass Gift Subs

Alert actions can include:

- Chat messages
- Images
- Videos
- Sounds
- Text overlays
- Discord notifications

All powered by Twitch EventSub.

---

## 🎟️ Channel Point Rewards

Connect any existing Twitch Channel Point reward to a custom action chain.

Supported tokens include:

```text
{user}
{reward_title}
{cost}
{user_input}
```

Reward redemptions are detected instantly using EventSub.

---

## 💬 Commands

Create custom commands with permission controls.

Supported roles:

- Everyone
- Subscriber
- VIP
- Moderator
- Broadcaster

Built-in examples:

```text
!uptime
!followage
!shoutout
!discord
!socials
!commands
```

Commands can trigger overlays, sounds, Discord posts and other action chains.

---

## 🛡️ Twitch Moderation

Protect your community with:

- Warning systems
- Strike ladders
- Automatic timeouts
- Automatic bans
- Banned words
- Import / Export support

Configure unlimited moderation levels.

---

## 🎥 OBS Overlays

SnapShield hosts browser overlays locally for OBS.

Features include:

- Images
- Videos
- GIFs
- Text
- Animated entrances and exits
- Avatar integration
- Sound playback

Default overlay:

```text
http://127.0.0.1:5757/overlay/default
```

---

## 🎮 Mini Games

Included games:

### 🎰 Slots

Custom payouts and betting limits.

### 🪙 Coin Flip

Heads or tails.

### 🎲 High / Low Dice

Guess higher or lower.

### 🔮 8 Ball

Random answers for viewers.

### 💰 Economy

Built-in:

- !balance
- !daily
- Statistics tracking

---

## 🌐 Discord Integration

SnapShield connects directly to Discord using OAuth.

No Discord bot token required.

Features:

- Alert notifications
- Twitch clips
- Stream summaries
- Action-chain messages
- Multi-channel support

---

## 🎵 Music Features

Supports:

- Spotify
- YouTube Music
- Local Basic Player

Available tools:

- Song Requests
- Now Playing
- Queue
- Skip Song
- Auto Announcements

Song Request tokens:

```text
{track}
{artist}
{album}
{duration}
{url}
{requested_by}
```

---

# 📸 Screenshots

Add screenshots here:

```md
docs/images/dashboard.png

!ocs/images/commands.png

!ocs/images/action-chains.png

!ocs/images/overlays.png
```

---

# ⚡ Quick Start

## Download

Grab the latest release:

```text
https://github.com/Snapten/SnapShield/releases
```

## Install

Run:

```text
SnapShield-Setup-x.x.x.exe
```

## Login

1. Log in with your Streamer account
2. (Optional) Log in with a Bot account
3. Connect Twitch
4. Start building alerts and commands

Done.

---

# 🏗️ Project Structure

```text
SnapShield/
├── bot/
├── ui/
├── storage/
├── data/
├── assets/
├── logs/
├── main.py
└── requirements.txt
```

---

# 🔑 Twitch Authentication

SnapShield uses Twitch's Device Code authentication flow.

No client secret is required.

1. Click "Log in with Streamer Account"
2. Visit twitch.tv/activate
3. Enter the code shown
4. Authorise access

Optionally connect a dedicated Bot account.

---

# 🖥️ Running From Source

```bash
python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python main.py
```

---

# 📦 Building

Using the included spec file:

```bash
pyinstaller SnapShield.spec
```

Output:

```text
dist/SnapShield.exe
```

---

# 🔄 Automatic Updates

SnapShield includes a built-in updater.

Features:

- Startup update checks
- SHA-256 verification
- Automatic restart
- Rollback support
- AppData-safe updates

User settings remain untouched during upgrades.

---

# 🔒 Security Notes

- Discord OAuth tokens remain local.
- Discord webhooks are stored inside the data folder.
- Twitch OAuth refreshes occur automatically.
- No cloud-hosted SnapShield services are required.

---

# 📄 Data Storage

All configuration is saved in JSON files.

Examples:

```text
data/
├── twitch_accounts.json
├── twitch_alerts.json
├── twitch_commands.json
├── twitch_moderation.json
├── channel_points.json
├── gamedata.json
└── music_accounts.json
```

---

# 🛣️ Roadmap

- More overlay animations
- Additional Twitch integrations
- Expanded music providers
- More mini-games
- Enhanced analytics

---

# 🤝 Contributing

Contributions, feature ideas and bug reports are welcome.

Please open an Issue or Pull Request.

---

# 📜 License

Copyright © Snapten

All rights reserved.
``
