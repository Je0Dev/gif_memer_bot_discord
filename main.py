import asyncio
import logging
import os
from typing import Optional

import aiohttp
import discord
from discord.ext import commands, ipc
from dotenv import load_dotenv
from quart import Quart
from quart import jsonify
from quart_cors import cors

from config import validate_environment
from logging_config import setup_logging

load_dotenv()

env_config = validate_environment()
logger = setup_logging(log_level=env_config.log_level)


class MemeBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

        self.ipc_server: Optional[ipc.Server] = None
        self.app: Optional[Quart] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

        self._setup_ipc()

    def _setup_ipc(self) -> None:
        self.ipc_server = ipc.Server(self, secret_key=env_config.ipc_secret_key)

    async def setup_hook(self) -> None:
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        await self.load_extension("cogs.memes")
        await self.load_extension("cogs.settings")
        await self.load_extension("cogs.dashboard")
        await self.tree.sync()
        logger.info("Slash commands synced.")

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        if self.ipc_server:
            await self.ipc_server.start()

    async def close(self) -> None:
        if self.http_session:
            await self.http_session.close()
        await super().close()


bot = MemeBot()

app = Quart(__name__)
app = cors(app, allow_origin="*")

app.secret_key = env_config.quart_secret_key
app.config["DISCORD_CLIENT_ID"] = env_config.discord_client_id
app.config["DISCORD_CLIENT_SECRET"] = env_config.discord_client_secret
app.config["DISCORD_REDIRECT_URI"] = env_config.discord_redirect_uri
app.config["DISCORD_BOT_TOKEN"] = env_config.discord_token

bot.app = app

import quart_discord

discord_oauth = quart_discord.DiscordOAuth2Session(app)
bot.discord_oauth = discord_oauth


@app.errorhandler(Exception)
async def handle_exception(e: Exception) -> tuple[dict, int]:
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


@app.route("/health")
async def health_check() -> tuple[dict, int]:
    status = {
        "status": "healthy",
        "bot_ready": bot.is_ready(),
        "guilds": len(bot.guilds),
    }
    return status, 200


@app.route("/api/guilds")
async def api_guilds() -> tuple[dict, int]:
    if not bot.is_ready():
        return {"error": "Bot not ready"}, 503

    guilds_data = [
        {"id": guild.id, "name": guild.name, "member_count": guild.member_count}
        for guild in bot.guilds
    ]
    return {"guilds": guilds_data}, 200


async def run_bot() -> None:
    await bot.start(env_config.discord_token)


async def run_dashboard() -> None:
    await app.run_task(host="0.0.0.0", port=5000)


async def main() -> None:
    try:
        await asyncio.gather(run_bot(), run_dashboard())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
