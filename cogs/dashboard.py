import os
from quart import render_template, redirect, url_for, request
from discord.ext import commands, ipc

class Dashboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = bot.app
        self.discord_oauth = bot.discord_oauth
        self.ipc_client = ipc.Client(secret_key=os.getenv("IPC_SECRET_KEY", "supersecretipc"))
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/")
        async def index():
            return await render_template("index.html")

        @self.app.route("/login")
        async def login():
            return await self.discord_oauth.create_session(scope=["identify", "guilds"])

        @self.app.route("/callback")
        async def callback():
            await self.discord_oauth.callback()
            return redirect(url_for("servers"))

        @self.app.route("/servers")
        async def servers():
            if not await self.discord_oauth.authorized():
                return redirect(url_for("login"))
            
            user = await self.discord_oauth.fetch_user()
            guilds = await self.discord_oauth.fetch_guilds()
            
            # Filter: User has Manage Server AND Bot is in the guild
            bot_guild_ids = {g.id for g in self.bot.guilds}
            manageable_guilds = [g for g in guilds if g.permissions.manage_guild and g.id in bot_guild_ids]
            
            return await render_template("servers.html", user=user, guilds=manageable_guilds)

        @self.app.route("/server/<int:guild_id>/settings")
        async def server_settings(guild_id):
            if not await self.discord_oauth.authorized():
                return redirect(url_for("login"))
                
            # Fetch settings via IPC
            settings = await self.ipc_client.request("get_guild_settings", guild_id=guild_id)
            
            # Fetch text channels for dropdown
            guild = self.bot.get_guild(guild_id)
            channels = [{"id": c.id, "name": c.name} for c in guild.text_channels] if guild else []
            
            return await render_template("server_settings.html", guild_id=guild_id, settings=settings, channels=channels)

        @self.app.route("/server/<int:guild_id>/settings", methods=["POST"])
        async def update_settings(guild_id):
            form = await request.form
            daily_memes = form.get("daily_memes") == "on"
            target_channel_id = form.get("target_channel")
            target_channel_id = int(target_channel_id) if target_channel_id else None
            
            await self.ipc_client.request("update_guild_settings", guild_id=guild_id, daily_memes=daily_memes, target_channel_id=target_channel_id)
            return redirect(url_for("server_settings", guild_id=guild_id))

    async def cog_load(self):
        await self.ipc_client.start()

    async def cog_unload(self):
        await self.ipc_client.close()

async def setup(bot):
    await bot.add_cog(Dashboard(bot))
