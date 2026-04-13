# Meme Bot & Web Dashboard

A professional Discord bot built with `discord.py` featuring meme and GIF commands, paired with a modern web dashboard built using `Quart` and `Quart-Discord`. The bot and dashboard communicate seamlessly via Inter-Process Communication (IPC) to manage server settings in real-time.

## Features

### Discord Bot
- **Slash Commands**: Fully integrated app commands (`/meme`, `/memes`, `/dankmemes`, `/me_irl`, `/wholesome`, `/memehub`, `/memesub`, `/gif`, `/gifs`, `/trending`, `/sticker`, `/random`).
- **Multi-Provider GIF System**: Fetches GIFs from Klipy, with automatic fallback to Giphy → Tenor if previous providers fail.
- **Meme Fetching**: Retrieves random memes from Reddit via a public API (multiple subreddits: memes, dankmemes, me_irl, wholesomememes, MemeHub).
- **Asynchronous Architecture**: Uses `aiohttp` for fast, non-blocking web requests with proper timeout handling.
- **Robust Error Handling**: Graceful fallbacks, user-friendly ephemeral messages, and detailed console logging.

### Web Dashboard
- **Discord OAuth2 Login**: Secure authentication using Discord accounts.
- **Server Management**: View servers where you have "Manage Server" permissions and the bot is currently present.
- **Real-time Settings**: Toggle "Daily Memes" and select a target channel for each server via a clean UI.
- **IPC Integration**: Communicates directly with the running bot to fetch/update settings without restarting or direct DB access from the web layer.
- **Rate Limiting**: Built-in protection against abuse.
- **Health Check Endpoint**: Monitor bot status programmatically.

### Data Persistence
- **SQLite Database**: Stores guild preferences (daily meme toggles, target channels) using `aiosqlite` with async-safe operations.

## Tech Stack

- **Bot Framework**: `discord.py` (v2+)
- **Web Framework**: `Quart` (Async Flask alternative)
- **Authentication**: `Quart-Discord`
- **IPC**: `discord-ext-ipc`
- **Database**: `aiosqlite`
- **HTTP Client**: `aiohttp`
- **Rate Limiting**: `slowapi`
- **Testing**: `pytest`, `pytest-asyncio`
- **Code Quality**: `black`, `ruff`, `mypy`, `isort`

## Prerequisites

- Python 3.9+
- A Discord Bot Token
- Discord Application Client ID & Secret
- Klipy API Key (optional, recommended for primary GIF source)
- Giphy API Key (fallback GIF provider)

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Je0Dev/gif_memer_bot_discord.git
cd gif_memer_bot_discord
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | Yes |
| `DISCORD_CLIENT_ID` | Discord OAuth2 Client ID | Yes |
| `DISCORD_CLIENT_SECRET` | Discord OAuth2 Client Secret | Yes |
| `DISCORD_REDIRECT_URI` | OAuth2 callback URL | No (default provided) |
| `KLIPY_API_KEY` | Klipy GIF API key | Recommended |
| `GIPHY_API_KEY` | Giphy API key | Fallback |
| `IPC_SECRET_KEY` | IPC communication secret | Yes |
| `QUART_SECRET_KEY` | Web session secret | Yes |
| `DATABASE_URL` | SQLite database path | No (default provided) |
| `LOG_LEVEL` | Logging verbosity | No (default: INFO) |

### 3. Run the Bot

```bash
python main.py
```

This starts both the Discord bot and web dashboard concurrently.

- **Bot**: Connects to Discord and registers slash commands
- **Dashboard**: Available at `http://localhost:5000`

### 4. Invite Bot to Your Discord Server

To add this bot to your Discord server, you need to create an invite link with the correct permissions.

#### Option A: Using the OAuth2 URL Generator

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Click **OAuth2** in the left sidebar, then **URL Generator**
4. In the **Scopes** section, check:
   - `bot`
   - `applications.commands`
5. In the **Bot Permissions** section, check:
   - **Text Permissions**:
     - `Send Messages`
     - `Read Message History`
     - `Embed Links`
6. Copy the generated **OAuth2 URL** at the bottom
7. Paste the URL into your browser and select which server to add the bot to

#### Option B: Direct Invite Link

Replace `YOUR_CLIENT_ID` with your bot's Application ID:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=67488832&scope=bot%20applications.commands
```

**Required Permissions:**
| Permission | Value | Reason |
|------------|-------|--------|
| Send Messages | 0x800 | Bot can send meme/GIF embeds |
| Read Message History | 0x10000 | Required for some features |
| Embed Links | 0x4000 | Allows rich embeds |

#### After Inviting the Bot

Once the bot is in your server:
1. Start the bot: `python main.py`
2. The bot will register slash commands automatically
3. Use `/meme` or `/gif <query>` to test

## Docker Deployment

### Using Docker Compose

```bash
# Set environment variables
export DISCORD_TOKEN=your_token
export DISCORD_CLIENT_ID=your_client_id
export DISCORD_CLIENT_SECRET=your_secret
export IPC_SECRET_KEY=your_ipc_key
export QUART_SECRET_KEY=your_quart_key
export KLIPY_API_KEY=your_klipy_key
export GIPHY_API_KEY=your_giphy_key

# Start the container
docker-compose up -d
```

### Using Dockerfile

```bash
docker build -t meme-bot .
docker run -d --env-file .env meme-bot
```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Je0Dev/gif_memer_bot_discord.git
cd gif_memer_bot_discord

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cogs --cov=main --cov-report=html

# Run specific test file
pytest tests/test_memes.py

# Run only unit tests (exclude integration)
pytest -m "not integration"

# Watch mode
pytest --watch
```

### Code Quality Checks

```bash
# Run all linters
ruff check .

# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Run pre-commit on all files
pre-commit run --all-files
```

## Project Structure

```
discord_gif_bot/
├── cogs/                    # Discord bot extensions
│   ├── memes.py            # Meme & GIF commands
│   ├── settings.py        # Database & IPC handlers
│   └── dashboard.py       # Web dashboard routes
├── templates/              # Jinja2 templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── servers.html       # Server list
│   └── server_settings.html
├── static/                 # Static assets
├── tests/                  # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_memes.py
│   ├── test_settings.py
│   └── test_dashboard.py
├── logs/                   # Log files (created at runtime)
├── main.py                # Entry point
├── config.py              # Environment validation
├── logging_config.py      # Logging setup
├── pyproject.toml         # Project configuration
├── pytest.ini             # Test configuration
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/login` | GET | Initiate Discord OAuth |
| `/callback` | GET | OAuth callback |
| `/servers` | GET | List manageable servers |
| `/server/<id>/settings` | GET | Server settings page |
| `/server/<id>/settings` | POST | Update server settings |
| `/health` | GET | Health check (rate limited: 100/min) |
| `/api/guilds` | GET | Bot guild info (rate limited: 60/min) |

### Health Check Response

```json
{
  "status": "healthy",
  "bot_ready": true,
  "guilds": 42
}
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/meme` | Fetch a random meme from Reddit (default: r/memes) |
| `/memes [count]` | Fetch multiple random memes (1-10) |
| `/dankmemes` | Fetch from r/dankmemes |
| `/me_irl` | Fetch from r/me_irl |
| `/wholesome` | Fetch wholesome memes from r/wholesomememes |
| `/memehub` | Fetch from r/MemeHub |
| `/memesub <subreddit>` | Fetch from a specific subreddit |
| `/gif <query>` | Search for GIFs (defaults to "trending") |
| `/gifs <query> [count]` | Fetch multiple GIFs (1-10) |
| `/trending` | Trending GIFs from Giphy |
| `/sticker <query>` | Search for stickers |
| `/random [type]` | Random command (meme, gif, dankmemes, wholesome, me_irl, memehub) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and commit conventions.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
