<p align="center">
  <img width="200" height="200" alt="snapshield" src="https://github.com/user-attachments/assets/accdea01-0ae6-47eb-8962-00e2e663ef4d" />
</p>


<p align="center">
A powerful Windows desktop suite for Twitch streamers: overlays, alerts, moderation,
channel points, giveaways, subathons, counters, music tools, overlay games with chat betting and more.
Powered by Twitch EventSub.
</p>

<p align="center">
  <a href="https://dev.twitch.tv/docs/eventsub/"><img src="https://img.shields.io/badge/Twitch-EventSub-9146FF?style=for-the-badge&logo=twitch&logoColor=white" alt="Twitch EventSub"></a>
  <a href="https://www.microsoft.com/windows"><img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"></a>
</p>

<p align="center">
  <a href="https://snapshield.snapten.uk">Website</a> •
  <a href="https://github.com/Snapten/Snapshield/releases">Releases</a> •
  <a href="https://webshield.snapten.uk">WebShield Dashboard</a>
</p>

---

## ✨ What is SnapShield?

SnapShield is a locally-hosted Twitch automation app for streamers who want powerful tools **without cloud services or monthly subscriptions**. Everything runs on your own PC.

✅ Twitch Alerts
✅ Local OBS Overlays *(`127.0.0.1:5757`)*
✅ Channel Point Automations
✅ Chat Commands
✅ Giveaways: random winners, spin-reel reveal, 8 overlay themes
✅ Subathon: extendable countdown clock
✅ Counters, timers and countdowns
✅ Live chat panel: read and reply as streamer or bot, with quick-action widgets
✅ Overlay games: Snake Invaders, SnapFight and Horse Racing (with coin betting)
✅ Twitch Moderation and global blacklist protection
✅ Discord Login: send clips and alerts to your channels
✅ Clip Creation
✅ Music Integration
✅ Mini Games & Economy (one shared coin wallet across every game)
✅ Installer and one-click updates

> **Two products, one family.** SnapShield is the **Twitch-only desktop app**.
> Discord server moderation and community tools live in **WebShield**, a separate hosted dashboard at **[webshield.snapten.uk](https://webshield.snapten.uk)**. See [SnapShield vs WebShield](#-snapshield-vs-webshield).

---

## 🆚 SnapShield vs WebShield

| | **SnapShield** (this repo) | **WebShield** |
|---|---|---|
| What it is | Windows desktop app | Hosted Discord dashboard |
| Platform | Twitch | Discord |
| Runs | On your PC | In your browser |
| Handles | Alerts, overlays, channel points, giveaways, subathon, counters, games, music, Twitch moderation | Discord server moderation and community management |
| Get it | [Releases](https://github.com/Snapten/Snapshield/releases) | [webshield.snapten.uk](https://webshield.snapten.uk) |

The desktop app still connects to Discord through a simple **Discord login** so it can post clips, alerts and summaries into your channels. It does not run a Discord bot.

---

## 🚀 Why SnapShield?

Unlike traditional Twitch bots, SnapShield combines multiple streaming tools into a single desktop app.

| Feature | SnapShield |
|---|---|
| Native Windows App | ✅ |
| No Monthly Subscription | ✅ |
| Local OBS Browser Overlays | ✅ |
| Twitch EventSub Powered | ✅ |
| Built‑in Giveaways, Subathon & Counters | ✅ |
| Built‑in Overlay Games with chat betting | ✅ |
| Live Chat Panel with Widgets | ✅ |
| Built‑in Mini Games & Economy | ✅ |
| Discord OAuth Integration (no bot token) | ✅ |
| Installer + Update Prompt | ✅ |
| Fully Custom Action Chains | ✅ |

---

## 🎬 Core Features

### ⚙️ Action Chains: The Heart of SnapShield
Build visual workflows reused across alerts, commands, rewards and the Basic Player:

| Action | Description |
|---|---|
| 💬 Chat Message | Send Twitch messages |
| 🖼️ Overlay Media | Images, videos, avatars |
| 📝 Text Overlay | Styled text with animations |
| 🔊 Sound | Play audio effects |
| 🎮 Command | Trigger another command (e.g. auto shout-out the raider on a raid) |
| 🌐 Discord | Post to your connected Discord channels |
| 🛡️ Moderation | Warn, timeout, ban |
| ⏳ Wait | Pause before next action |

---

### 📢 Twitch Alerts
Custom automated reactions for:
- Follows • Raids • New Subs • Gifted Subs • Mass Gift Subs

Actions: chat messages, images, videos, sounds, text overlays, Discord notifications, all via **Twitch EventSub**.

---

## 🏘️ Community

Everything audience-facing lives under the **Community** page.

### 🎁 Giveaways
Run fully featured giveaways from the app or chat:
- Enter via `!join` **or** a channel point redemption (SnapShield creates the reward for you)
- 8 overlay themes with customisable colours, fonts and layout
- Spinning-reel winner reveal with scrolling names
- Winners claim with `!win` or skip with `!skipme` → auto‑redraw
- Optional **follow requirement** (minimum days following), plus sub/VIP restrictions
- Customisable chat messages

| Mod commands | |
|---|---|
| `!giv start` / `startredeem` | Open entries (chat or channel points) |
| `!giv pick` | Draw a winner |
| `!giv time` | Change the entry time |
| `!giv pause` / `resume` | Pause and resume entries |
| `!giv reset` / `reopen` | Reset or reopen |
| `!giv ignore` / `unignore` | Exclude or include a user |
| `!giv ban` / `unban` | Ban or unban a user from entering |

Viewers use `!join`, `!unjoin`, `!win` and `!skipme`.

### ⏱️ Subathon
A live countdown viewers extend in real time:
- Add time from Follows • Subs (T1/T2/T3) • Gifted Subs • Bits • Raids
- Every amount is editable (for example follows add 10s, subs add 30s)
- Channel point rewards that add time (for example 5000 points = 10s)
- Themed overlay with time bar, top supporters and pop-ups like “{user} followed and added 10s”
- Multiplier mode (`x2`), max cap and pause controls
- Clock is saved across app restarts
- Viewer command: `!subtime` • Mod: `!subathon start 3h`

### 🔢 Counters
Create **counters**, **timers** and **countdowns** with their own overlays:
- Counters like `!deaths` that mods can add to
- Countdowns viewers can add time to with channel points *(off by default)*
- Choose who can use each one: Everyone • Followers • Subscribers • VIPs • Mods
- Banner on/off and overlay selection per item

### 🐍 Snake Invaders *(overlay game)*
Chat joins a snake that crawls down the screen while cannons shoot at it.
- Starts with 4 free sections plus a head, then 1 section per joiner
- The snake starts at the top and must reach the bottom to win; cannons fire straight up like the arcade classic
- Each section can show the joiner's **Twitch avatar**, name or both
- Easy / Normal / Hard difficulty and 4 to 6 cannons
- Everyone who joined wins **Basic Games coins** when the snake wins (amount settable, default 100)
- Sound effects with an on/off tick box and volume slider
- Start it with a **channel point reward** or the mod command

### 🥊 SnapFight *(overlay game)*
A red fighter and a blue fighter punch, kick and uppercut on your overlay, and chat **bets on the winner**:
- Start a fight with a **channel point reward**, the `!fight` mod command or the page buttons
- Bet with `!red` / `!blue`, optionally with an amount (`!red 100`, `!blue all`); **minimum and maximum bet are settings**
- Best of three rounds with health bars, KOs and a hidden per-fight "form" so the result is a real gamble
- Fixed-multiplier or shared-pool payouts into the Basic Games wallet; bets are refunded if a fight is stopped
- Built-in arenas (Arena, Dojo, Neon city), **upload your own background**, or go **transparent**
- Rename the fighters, change their colours, and enable sound effects

### 🏇 Horse Racing *(overlay game)*
A virtual race with a proper **betting slip**:
- Up to nine runners with silks, horse names, jockeys and real fractional odds like `8/1`
- Bet with `!horse 3 100`; the first three home all pay (1st at the full odds, 2nd and 3rd at a share, all settable)
- A 30-second race, a rare **photo finish** with a suspenseful wait, a **slow-motion replay** and a podium result screen
- Your own editable lists of horse names, jockeys, racecourses and race times
- Starts from a channel point reward, `!race` mod command or the page buttons, with sound effects

### 🎮 Mini Games & Economy
- 🎰 Slots • 🪙 Coin Flip • 🎲 High/Low Dice • 🔮 8‑Ball
- Built‑in economy: `!balance` `!daily` and stats tracking
- The same coin wallet is used by Snake Invaders, SnapFight and Horse Racing

---

### 💬 Live Chat Panel
A chat box on its own page so you can run the stream from SnapShield:
- Read chat and reply as the **streamer or the bot**
- Optional **widgets** beside the chat that you can drag, reorder and remove: Basic Player play/stop and skip, Shield mode on/off, an activity feed and more
- Adjustable chat font size for readability

### 🎟️ Channel Point Rewards
Link rewards to Action Chains instantly via EventSub.
Available tokens:
```
{user} {reward_title} {cost} {user_input}
```

---

### 💬 Chat Commands
Custom commands with role permissions:
- Everyone • Subscriber • VIP • Moderator • Broadcaster

Built‑ins: `!uptime` `!followage` `!shoutout` `!discord` `!socials` `!commands`
Commands live in **Community → Commands**, and any command can be run from an Action Chain (for example, an Incoming Raid alert that runs `!shoutout` for the raider).
Plus the giveaway, subathon, counter and game commands above.

---

### 🛡️ Twitch Moderation
- Warning systems • Strike ladders • Auto timeouts/bans
- Banned word filtering • Import/Export • Unlimited custom levels
- **Global blacklist** check with status notifications (checking, updating, ready, out of date) and a Diagnostics indicator

---

### 🎥 Local OBS Overlays
Hosted directly on your PC, no external server needed:
```
http://127.0.0.1:5757/overlay/default
```
The overlay server only listens on your own machine (`127.0.0.1`). Supports images, videos, GIFs, styled text, animated in/out, avatars and audio, plus dedicated overlays for giveaways, subathon, counters and the games.

---

### 🌐 Discord Login
Connect with **Discord OAuth**; no bot token required and nothing to host:
- Choose which channels SnapShield may post to
- Alert notifications • Clip sharing • Stream summaries • Action‑Chain posts
- Optional auto-post of every clip as an embed
- Multi‑channel support

For full Discord server moderation, use **[WebShield](https://webshield.snapten.uk)**.

---

### 🎵 Music Features
Spotify • YouTube Music • Basic (local) Player
- Song requests (Spotify queue / YouTube playlist)
- `Now Playing`, `Queue` and moderator `Skip` commands, plus auto‑announce on track change
- Playback device picker for Spotify and the Basic Player
- Basic Player reads ID3 tags and runs its own Action Chain on every track start
- Tokens: `{track}` `{artist}` `{duration}` `{requested_by}`

> Spotify's Development Mode requires a Spotify Premium account for any authorised account.

---

## 📸 Screenshots

Screenshots live in `docs/images/`:
`dashboard.png` • `commands.png` • `action-chains.png` • `overlays.png` • `giveaways.png` • `subathon.png`

---

## ⚡ Quick Start

### Download
Grab the latest release from the [Releases page](https://github.com/Snapten/Snapshield/releases) or the **Download** button at **https://snapshield.snapten.uk**.

### Install
Run the installer (`SnapShield-Setup-<version>.exe`).
*(No admin rights required. It installs per user so the updater can replace files.)*

### Login & Connect
1. Log in with your **Streamer Account**
2. *(Optional)* Connect a dedicated **Bot Account**
3. Authorise at `twitch.tv/activate`
4. *(Optional)* Open the **Discord** page and log in to choose channels for clips and alerts
5. Start building alerts, giveaways, subathon, counters and games. Done!

> Windows "protected your PC" or "Unknown publisher"? Click **More info** → **Run anyway**. SnapShield is not yet code-signed.

---

## 💾 Where Your Data Lives

Settings, data, logs and update files are stored in `%APPDATA%\SnapShield`, not next to the exe, so they survive updates and reinstalls.

- Uninstalling asks before deleting your settings
- **Portable mode:** put a `portable.txt` file beside the exe, or set the `SNAPSHIELD_DATA_DIR` environment variable, to choose where data is kept
- **Diagnostics** page: backup, snapshot, import, and a **Reset All Settings** button (with a 30-second auto-cancelling confirmation)

---

## 🔄 Updates

- A few seconds after launch SnapShield checks for a new version and asks **Update now / Later**
- It never restarts mid-stream on its own
- Downloads are verified before install, with backup and rollback if something goes wrong
- A sidebar notice shows when an update is available
- Update details are written to `updater.log`

---

## 🔐 Staying Logged In

SnapShield uses a public Twitch application and refreshes tokens silently in the background, so there are no forced disconnects every few hours.

---

## 🛣️ Roadmap
- [ ] More overlay animations & themes
- [ ] Additional Twitch event integrations
- [ ] Expanded music providers
- [ ] More mini‑games
- [ ] Enhanced analytics & dashboard stats
- [ ] Export/share config presets
- [ ] Code signing for the Windows installer

---

## 🤝 Contributing
Found a bug or have an idea? Issues and feature requests are welcome!

## 📜 License
Copyright © Snapten. All Rights Reserved.
