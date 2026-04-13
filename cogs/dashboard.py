import logging
import os
from typing import Any, Optional

from discord.ext import commands, ipc
from quart import Quart, redirect, render_template, request, url_for


class Dashboard(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.app: Optional[Quart] = bot.app
        self.discord_oauth = bot.discord_oauth
        self.ipc_client = ipc.Client(
            secret_key=os.getenv("IPC_SECRET_KEY", "supersecretipc")
        )
        if bot.app:
            self._register_routes()

    def _register_routes(self) -> None:
        if not self.app:
            return

        @self.app.route("/")
        async def index() -> str:
            return await render_template("index.html")

        @self.app.route("/login")
        async def login() -> Any:
            return await self.discord_oauth.create_session(scope=["identify", "guilds"])

        @self.app.route("/callback")
        async def callback() -> Any:
            try:
                await self.discord_oauth.callback()
            except Exception as e:
                logging.error(f"OAuth callback failed: {e}")
                return "Authentication failed", 400
            return redirect(url_for("servers"))

        @self.app.route("/servers")
        async def servers() -> Any:
            if not await self.discord_oauth.authorized:
                return redirect(url_for("login"))

            try:
                user = await self.discord_oauth.fetch_user()
                guilds = await self.discord_oauth.fetch_guilds()

                bot_guild_ids = {g.id for g in self.bot.guilds}
                manageable_guilds = []
                for g in guilds:
                    perms = getattr(g, "permissions", 0)
                    if isinstance(perms, int):
                        has_manage = (perms & (1 << 5)) != 0
                    else:
                        has_manage = getattr(perms, "manage_guild", False)

                    if has_manage and g.id in bot_guild_ids:
                        manageable_guilds.append(g)

                return await render_template(
                    "servers.html", user=user, guilds=manageable_guilds
                )
            except Exception as e:
                logging.error(f"Error fetching servers: {e}")
                return "Failed to load servers", 500

        @self.app.route("/server/<int:guild_id>/settings")
        async def server_settings(guild_id: int) -> Any:
            if not await self.discord_oauth.authorized:
                return redirect(url_for("login"))

            try:
                settings = await self.ipc_client.request(
                    "get_guild_settings", guild_id=guild_id
                )
                if settings.get("error"):
                    logging.warning(f"IPC error fetching settings: {settings['error']}")
                    settings = {"daily_memes": False, "target_channel_id": None}
            except Exception as e:
                logging.error(f"IPC request failed: {e}")
                settings = {"daily_memes": False, "target_channel_id": None}

            guild = self.bot.get_guild(guild_id)
            channels = (
                [{"id": c.id, "name": c.name} for c in guild.text_channels]
                if guild
                else []
            )

            return await render_template(
                "server_settings.html",
                guild_id=guild_id,
                settings=settings,
                channels=channels,
            )

        @self.app.route("/server/<int:guild_id>/settings", methods=["POST"])
        async def update_settings(guild_id: int) -> Any:
            try:
                form = await request.form
                daily_memes = form.get("daily_memes") == "on"
                target_channel_id = form.get("target_channel")
                target_channel_id = (
                    int(target_channel_id) if target_channel_id else None
                )

                await self.ipc_client.request(
                    "update_guild_settings",
                    guild_id=guild_id,
                    daily_memes=daily_memes,
                    target_channel_id=target_channel_id,
                )
            except Exception as e:
                logging.error(f"Failed to update settings: {e}")
            return redirect(url_for("server_settings", guild_id=guild_id))

    async def cog_load(self) -> None:
        pass

    async def cog_unload(self) -> None:
        pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dashboard(bot))
