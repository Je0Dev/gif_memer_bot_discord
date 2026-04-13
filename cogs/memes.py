import logging
import os
import random
from typing import Any, Optional

import aiohttp
import discord
from discord.app_commands import describe
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None

    async def cog_load(self) -> None:
        if not self.bot.http_session:
            self.bot.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        self.session = self.bot.http_session

    async def cog_unload(self) -> None:
        pass

    @commands.hybrid_command(name="meme")
    @describe(description="Fetch a random meme from Reddit")
    async def meme(self, ctx: commands.Context[commands.Bot]) -> None:
        try:
            async with self.session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data: dict[str, Any] = await resp.json()
                    embed = discord.Embed(
                        title=data.get("title", "Meme"), color=discord.Color.random()
                    )
                    embed.set_image(url=data.get("url"))
                    embed.set_footer(
                        text=f"r/{data.get('subreddit', 'unknown')} | 👍 {data.get('ups', 0)}"
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(
                        "❌ Failed to fetch a meme. Please try again later.",
                        ephemeral=True,
                    )
        except (aiohttp.ClientError, TimeoutError) as e:
            logging.error(f"Meme command failed: {e}")
            await ctx.send(
                "❌ An error occurred while fetching the meme.", ephemeral=True
            )

    @commands.hybrid_command(name="gif")
    @describe(description="Fetch a random or searched GIF")
    async def gif(
        self, ctx: commands.Context[commands.Bot], *, query: str = "trending"
    ) -> None:
        klipy_key = os.getenv("KLIPY_API_KEY")
        giphy_key = os.getenv("GIPHY_API_KEY")

        if not klipy_key and not giphy_key:
            await ctx.send("⚠️ No GIF API keys configured.", ephemeral=True)
            return

        async def fetch_klipy() -> tuple[dict[str, Any], str] | None:
            if not klipy_key:
                return None
            try:
                async with self.session.get(
                    "https://api.klipy.com/v1/gifs/search",
                    params={"api_key": klipy_key, "q": query, "limit": 10},
                ) as resp:
                    if resp.status == 200:
                        data: dict[str, Any] = await resp.json()
                        results = data.get("data", [])
                        if results:
                            return random.choice(results), "Klipy"
            except Exception as e:
                logging.warning(f"Klipy request failed: {e}")
            return None

        async def fetch_giphy() -> tuple[dict[str, Any], str] | None:
            if not giphy_key:
                return None
            try:
                async with self.session.get(
                    "https://api.giphy.com/v1/gifs/search",
                    params={"api_key": giphy_key, "q": query, "limit": 10},
                ) as resp:
                    if resp.status == 200:
                        data: dict[str, Any] = await resp.json()
                        results = data.get("data", [])
                        if results:
                            return random.choice(results), "Giphy"
            except Exception as e:
                logging.warning(f"Giphy request failed: {e}")
            return None

        result = await fetch_klipy()
        if not result:
            logging.info("Klipy failed or returned no results, falling back to Giphy")
            result = await fetch_giphy()

        if result:
            gif_data, provider = result
            embed = discord.Embed(
                title=gif_data.get("title", "GIF"), color=discord.Color.random()
            )
            img_url = gif_data.get("url") or gif_data.get("images", {}).get(
                "original", {}
            ).get("url")
            if img_url:
                embed.set_image(url=img_url)
                embed.set_footer(text=f"Source: {provider}")
                await ctx.send(embed=embed)
                logging.info(f"GIF fetched via {provider}")
            else:
                await ctx.send(
                    "❌ Received invalid GIF data from provider.", ephemeral=True
                )
        else:
            await ctx.send(
                "Sorry, I couldn't find any GIFs right now. Please try again later!",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Memes(bot))
