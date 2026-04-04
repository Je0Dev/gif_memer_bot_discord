import aiosqlite
import os
from discord.ext import commands, ipc

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.getenv("DATABASE_URL", "sqlite:///bot_data.db").replace("sqlite:///", "")
        self.db = None

    async def cog_load(self):
        self.db = await aiosqlite.connect(self.db_path)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                daily_memes BOOLEAN DEFAULT 0,
                target_channel_id INTEGER
            )
        """)
        await self.db.commit()

    @ipc.server.route()
    async def get_guild_settings(self, data):
        guild_id = data.guild_id
        async with self.db.execute("SELECT daily_memes, target_channel_id FROM guild_settings WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"daily_memes": bool(row[0]), "target_channel_id": row[1]}
            return {"daily_memes": False, "target_channel_id": None}

    @ipc.server.route()
    async def update_guild_settings(self, data):
        guild_id = data.guild_id
        daily_memes = data.daily_memes
        target_channel_id = data.target_channel_id
        
        await self.db.execute("""
            INSERT INTO guild_settings (guild_id, daily_memes, target_channel_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET daily_memes=?, target_channel_id=?
        """, (guild_id, daily_memes, target_channel_id, daily_memes, target_channel_id))
        await self.db.commit()
        return {"status": "success"}

    async def cog_unload(self):
        if self.db:
            await self.db.close()

async def setup(bot):
    await bot.add_cog(Settings(bot))
