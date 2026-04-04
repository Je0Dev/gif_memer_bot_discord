# Meme Bot & Web Dashboard

A professional Discord bot built with `discord.py` featuring meme and GIF commands, paired with a modern web dashboard built using `Quart` and `Quart-Discord`. The bot and dashboard communicate seamlessly via Inter-Process Communication (IPC) to manage server settings in real-time.

## ✨ Features

### 🤖 Discord Bot
- **Slash Commands**: Fully integrated app commands (`/meme`, `/gif`).
- **Dual-Provider GIF System**: Fetches GIFs primarily from Klipy, with automatic fallback to Giphy if the primary fails or returns no results.
- **Meme Fetching**: Retrieves random memes from Reddit via a public API.
- **Asynchronous Architecture**: Uses `aiohttp` for fast, non-blocking web requests with proper timeout handling.
- **Robust Error Handling**: Graceful fallbacks, user-friendly ephemeral messages, and detailed console logging.

### 🌐 Web Dashboard
- **Discord OAuth2 Login**: Secure authentication using Discord accounts.
- **Server Management**: View servers where you have "Manage Server" permissions and the bot is currently present.
- **Real-time Settings**: Toggle "Daily Memes" and select a target channel for each server via a clean UI.
- **IPC Integration**: Communicates directly with the running bot to fetch/update settings without restarting or direct DB access from the web layer.

### 💾 Data Persistence
- **SQLite Database**: Stores guild preferences (daily meme toggles, target channels) using `aiosqlite` with async-safe operations.

## 🛠️ Tech Stack

- **Bot Framework**: `discord.py` (v2+)
- **Web Framework**: `Quart` (Async Flask alternative)
- **Authentication**: `Quart-Discord`
- **IPC**: `discord-ext-ipc`
- **Database**: `aiosqlite`
- **HTTP Client**: `aiohttp`
- **Testing**: `pytest`, `pytest-asyncio`

## 📋 Prerequisites

- Python 3.9+
- A Discord Bot Token
- Discord Application Client ID & Secret
- Klipy API Key (optional, but recommended)
- Giphy API Key (fallback provider)

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/meme-bot-dashboard.git
   cd meme-bot-dashboard
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy the example environment file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual API keys and tokens.

## ⚙️ Configuration

| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Your Discord bot token. |
| `DISCORD_CLIENT_ID` | Discord OAuth2 Client ID. |
| `DISCORD_CLIENT_SECRET` | Discord OAuth2 Client Secret. |
| `DISCORD_REDIRECT_URI` | OAuth2 callback URL (default: `http://localhost:5000/callback`). |
| `KLIPY_API_KEY` | API key for Klipy GIF service. |
| `GIPHY_API_KEY` | API key for Giphy GIF service. |
| `IPC_SECRET_KEY` | Secret key for secure IPC communication between bot and dashboard. |
| `QUART_SECRET_KEY` | Secret key for Quart session management. |
| `DATABASE_URL` | Path to the SQLite database (default: `sqlite:///bot_data.db`). |

## ▶️ Running the Application

Start both the Discord bot and the Quart web server concurrently:
