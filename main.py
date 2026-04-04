import os
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands, ipc
from quart import Quart
import quart_discord

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class MemeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)
        
        # IPC Server for dashboard communication
        self.ipc_server = ipc.Server(self, secret_key=os.getenv("IPC_SECRET_KEY", "supersecretipc"))
        
        # Placeholders for Quart app & OAuth session
        self.app = None
        self.discord_oauth = None

    async def on_ready(self):
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.ipc_server.start()

    async def setup_hook(self):
        await self.load_extension("cogs.memes")
        await self.load_extension("cogs.settings")
        await self.load_extension("cogs.dashboard")
        await self.tree.sync()
        logging.info("Slash commands synced.")

bot = MemeBot()

# Quart Web Dashboard Setup
app = Quart(__name__)
app.secret_key = os.getenv("QUART_SECRET_KEY", "supersecretquart")
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:5000/callback")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("DISCORD_TOKEN")

discord_oauth = quart_discord.DiscordOAuth2Session(app)

# Attach Quart components to bot for cog access
bot.app = app
bot.discord_oauth = discord_oauth

async def run_bot():
    await bot.start(os.getenv("DISCORD_TOKEN"))

async def run_dashboard():
    await app.run_task(host="0.0.0.0", port=5000)

async def main():
    # Run both the Discord bot and Quart server concurrently in the same event loop
    await asyncio.gather(run_bot(), run_dashboard())

if __name__ == "__main__":
    asyncio.run(main())
