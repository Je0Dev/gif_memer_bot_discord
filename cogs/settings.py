import logging
import os
from typing import Any, Optional

import aiosqlite
from discord.ext import commands, ipc


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_path = os.getenv("DATABASE_URL", "sqlite:///bot_data.db").replace(
            "sqlite:///", ""
        )
        self.db: Optional[aiosqlite.Connection] = None

    async def cog_load(self) -> None:
        try:
            self.db = await aiosqlite.connect(self.db_path)
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    daily_memes BOOLEAN DEFAULT 0,
                    target_channel_id INTEGER
                )
            """)
            await self.db.commit()
            logging.info("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")

    @ipc.server.route()
    async def get_guild_settings(self, data: Any) -> dict[str, Any]:
        try:
            guild_id = int(getattr(data, "guild_id", 0))
            if not guild_id:
                return {"error": "Invalid guild_id"}

            if self.db is None:
                return {"error": "Database not initialized"}

            async with self.db.execute(
                "SELECT daily_memes, target_channel_id FROM guild_settings WHERE guild_id = ?",
                (guild_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"daily_memes": bool(row[0]), "target_channel_id": row[1]}
                return {"daily_memes": False, "target_channel_id": None}
        except Exception as e:
            logging.error(f"Error fetching guild settings: {e}")
            return {"error": str(e)}

    @ipc.server.route()
    async def update_guild_settings(self, data: Any) -> dict[str, Any]:
        try:
            guild_id = int(getattr(data, "guild_id", 0))
            daily_memes = bool(getattr(data, "daily_memes", False))
            target_channel_id = getattr(data, "target_channel_id", None)
            if target_channel_id is not None:
                target_channel_id = int(target_channel_id)

            if self.db is None:
                return {"status": "error", "message": "Database not initialized"}

            await self.db.execute(
                """
                INSERT INTO guild_settings (guild_id, daily_memes, target_channel_id)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET daily_memes=?, target_channel_id=?
            """,
                (
                    guild_id,
                    daily_memes,
                    target_channel_id,
                    daily_memes,
                    target_channel_id,
                ),
            )
            await self.db.commit()
            return {"status": "success"}
        except Exception as e:
            logging.error(f"Error updating guild settings: {e}")
            return {"status": "error", "message": str(e)}

    async def cog_unload(self) -> None:
        if self.db:
            await self.db.close()
            logging.info("Database connection closed.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))
