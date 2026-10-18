# 🛡️ SnapShield

<p align="center">
A powerful desktop Twitch automation suite with overlays, alerts, moderation,
channel points, Discord integration, music tools, mini-games and more.
Built with Python, PyQt6 and Twitch EventSub.
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+"></a>
  <a href="https://www.riverbankcomputing.com/software/pyqt/"><img src="https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6"></a>
  <a href="https://dev.twitch.tv/docs/eventsub/"><img src="https://img.shields.io/badge/Twitch-EventSub-9146FF?style=for-the-badge&logo=twitch&logoColor=white" alt="Twitch EventSub"></a>
  <a href="https://www.microsoft.com/windows"><img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"></a>
</p>

---

## ✨ What is SnapShield?

SnapShield is a locally-hosted Twitch automation platform designed for streamers who want powerful tools **without cloud services or monthly subscriptions**. Everything runs on your own PC.

✅ Twitch Alerts
✅ OBS Overlays *(local: `127.0.0.1:5757`)*
✅ Channel Point Automations
✅ Chat Commands
✅ Giveaways — pick random winners, 8 overlay themes
✅ Subathon — extendable countdown clock via subs/follows/bits/raids
✅ Twitch Moderation
✅ Discord Integration
✅ Clip Creation
✅ Music Integration
✅ Mini Games & Economy
✅ Automatic Updates

---

## 🚀 Why SnapShield?

Unlike traditional Twitch bots, SnapShield combines multiple streaming tools into a single desktop app.

| Feature | SnapShield |
|---|---|
| Native Windows App | ✅ |
| No Monthly Subscription | ✅ |
| Local OBS Browser Overlays | ✅ |
| Twitch EventSub Powered | ✅ |
| Built‑in Giveaways & Subathon | ✅ |
| Built‑in Mini Games | ✅ |
| Discord OAuth Integration | ✅ |
| One‑Click Updater | ✅ |
| Fully Custom Action Chains | ✅ |

---

## 🎬 Core Features

### ⚙️ Action Chains — The Heart of SnapShield
Build visual workflows reused across alerts, commands, rewards:

| Action | Description |
|---|---|
| 💬 Chat Message | Send Twitch messages |
| 🖼️ Overlay Media | Images, videos, avatars |
| 📝 Text Overlay | Styled text with animations |
| 🔊 Sound | Play audio effects |
| 🎮 Command | Trigger another command |
| 🌐 Discord | Post to Discord channels |
| 🛡️ Moderation | Warn, timeout, ban |
| ⏳ Wait | Pause before next action |

---

### 📢 Twitch Alerts
Custom automated reactions for:
- Follows • Raids • New Subs • Gifted Subs • Mass Gift Subs

Actions: chat messages, images, videos, sounds, text overlays, Discord notifications — all via **Twitch EventSub**.

---

### 🎁 Giveaways *(New in v0.53.0)*
Run fully featured giveaways from the app or chat:
- Enter via `!join` command **or** channel point redemption
- 8 overlay themes — fully customisable colours, fonts, layout
- Auto‑draw winners with animated spin reveal
- Winners claim with `!win` or skip with `!skipme` → auto‑redraw
- Mod controls: pause, reopen, extend, ignore/ban users
- Restrict to subs/VIPs/followers; customise all chat messages

---

### ⏱️ Subathon *(New in v0.53.0)*
Live countdown viewers extend in real time:
- Add time from: Follows • Subs (T1/T2/T3) • Gifted Subs • Bits • Raids
- Channel point rewards → add time directly
- Customisable overlay with time bar, top supporters, pop‑ups
- Multiplier mode (`x2` time bonus), max cap, pause controls
- Persists across app restarts
- Viewer command: `!subtime` • Mod: `!subathon start 3h`

---

### 🎟️ Channel Point Rewards
Link rewards to Action Chains instantly via EventSub.
Available tokens:
{user} {reward_title} {cost} {user_input}
plaintext

---

### 💬 Chat Commands
Custom commands with role permissions:
- Everyone • Subscriber • VIP • Moderator • Broadcaster

Built‑ins: `!uptime` `!followage` `!shoutout` `!discord` `!socials` `!commands`
Plus: `!join` `!win` `!subtime` and full giveaway/subathon mod suites.

---

### 🛡️ Twitch Moderation
- Warning systems • Strike ladders • Auto timeouts/bans
- Banned word filtering • Import/Export • Unlimited custom levels

---

### 🎥 Local OBS Overlays
Hosted directly on your PC — no external server needed:
http://127.0.0.1:5757/overlay/default
plaintext
Supports: images, videos, GIFs, styled text, animated in/out, avatars, audio.

---

### 🎮 Mini Games & Economy
- 🎰 Slots • 🪙 Coin Flip • 🎲 High/Low Dice • 🔮 8‑Ball
- Built‑in economy: `!balance` `!daily` + stats tracking

---

### 🌐 Discord Integration
Connect via **Discord OAuth** — no bot token required:
- Alert notifications • Clip sharing • Stream summaries • Action‑Chain posts
- Multi‑channel support

---

### 🎵 Music Features
Spotify • YouTube Music • Local Player
- Song Requests • Now Playing • Queue • Skip • Auto‑Announce
- Tokens: `{track}` `{artist}` `{duration}` `{requested_by}`

---

## 📸 Screenshots
docs/images/dashboard.png
docs/images/commands.png
docs/images/action-chains.png
docs/images/overlays.png
docs/images/giveaways.png
docs/images/subathon.png
plaintext

---

## ⚡ Quick Start

### Download
Grab the latest release:
👉 **https://github.com/Snapten/SnapShield/releases**

### Install
Run:
SnapShield-Setup-0.53.0.exe
plaintext
*(No admin rights required — installs to your user folder)*

### Login & Connect
1. Log in with your **Streamer Account**
2. *(Optional)* Connect a dedicated **Bot Account**
3. Authorise at `twitch.tv/activate`
4. Start building alerts, giveaways, subathon — done!

> Windows "protected your PC"? Click **More info** → **Run anyway**

---

## 🏗️ Project Structure
SnapShield/
├── bot/
├── ui/
├── storage/
├── data/
├── assets/
├── logs/
├── main.py
└── requirements.txt
plaintext

---

## 🔄 Automatic Updates
Built‑in updater keeps your install fresh:
- Checks on startup → **Update Now / Later**
- SHA‑256 integrity verification • Auto‑restart • Rollback support
- Settings preserved in `%APPDATA%\SnapShield`

🛣️ Roadmap
 More overlay animations & themes
 Additional Twitch event integrations
 Expanded music providers
 More mini‑games
 Enhanced analytics & dashboard stats
 Export/share config presets

🤝 Contributing
Issues, feature ideas and pull requests welcome!

📜 License
Copyright © Snapten — All Rights Reserved
