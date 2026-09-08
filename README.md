# Snapshield - Multi-Platform Bot Management System

A unified backend API for Discord and Twitch bot management with web dashboard integration.

## 🌐 Access the Dashboard

```
http://localhost:5000
```

## Features

### Discord Bot
- OAuth authentication
- Moderation system (3-strike auto-ban)
- Custom command management
- Comprehensive event logging
- Multi-server support

### Twitch Bot
- Streamer & bot account authentication
- Event tracking (follows, subs, raids, bits)
- 3-strike moderation system
- Custom commands with permission levels

## Quick Start

### Prerequisites
- Python 3.10+
- Discord Bot Token
- Twitch Client ID & Secret

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API tokens

# Run the server
python app.py
```

### Environment Variables

```env
DISCORD_TOKEN=your_bot_token
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
FLASK_ENV=development
DATABASE_URL=sqlite:///snapshield.db
```

## API Endpoints

### Authentication
- `POST /api/auth/discord/login` - Initiate Discord OAuth
- `POST /api/auth/twitch/login` - Initiate Twitch OAuth
- `GET /api/auth/user` - Get current user info
- `POST /api/auth/logout` - Logout

### Commands
- `GET /api/commands` - List all commands
- `POST /api/commands` - Create command
- `PUT /api/commands/<id>` - Update command
- `DELETE /api/commands/<id>` - Delete command

### Moderation
- `GET /api/moderation/config` - Get moderation config
- `POST /api/moderation/config` - Update config
- `GET /api/moderation/logs` - Get moderation logs
- `POST /api/moderation/strike` - Add strike

## Database Models

- `User` - User accounts
- `DiscordAccount` - Linked Discord accounts
- `TwitchAccount` - Linked Twitch accounts
- `Command` - Custom commands
- `UserStrike` - Strike records
- `ModerationLog` - Action logs

## License

Proprietary - All rights reserved
