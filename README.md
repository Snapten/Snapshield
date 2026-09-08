# Snapshield - Multi-Platform Bot Management System

A unified bot management dashboard for Discord and Twitch with advanced moderation, command management, and event tracking.

## Features

### Discord Bot
- User authentication & account linking
- Moderation system (3-strike auto-ban)
- Custom command management
- Message/kick/ban logging
- Multi-account support with default account routing

### Twitch Bot
- Streamer & bot account authentication
- Follows and event tracking
- Moderation system (3-strike auto-ban)
- Custom command management
- Permission-based commands (streamer, mod, chat, VIP)

## Project Structure

```
snapshield/
├── frontend/
│   ├── pages/
│   │   ├── dashboard.html
│   │   ├── discord/
│   │   ├── twitch/
│   │   └── settings.html
│   ├── css/
│   ├── js/
│   └── index.html
├── backend/
│   ├── discord_bot/
│   ├── twitch_bot/
│   ├── api/
│   ├── database/
│   └── config/
├── requirements.txt
└── main.py
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure Discord and Twitch API credentials
3. Run the application: `python main.py`
