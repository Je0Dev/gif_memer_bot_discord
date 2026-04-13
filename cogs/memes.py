import logging
import os
import random
from collections import defaultdict
from typing import Any, Optional

import aiohttp
import discord
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None
        self.seen_memes: dict[str, set[str]] = defaultdict(set)
        self.seen_gifs: dict[str, set[str]] = defaultdict(set)
        self.meme_cache: list[dict[str, Any]] = []
        self.gif_cache: list[dict[str, Any]] = []

    async def cog_load(self) -> None:
        if not self.bot.http_session:
            self.bot.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        self.session = self.bot.http_session

    async def cog_unload(self) -> None:
        pass

    def _create_meme_embed(self, data: dict[str, Any]) -> discord.Embed:
        embed = discord.Embed(
            title=data.get("title", "Meme")[:256], color=discord.Color.random()
        )
        embed.set_image(url=data.get("url"))
        embed.set_footer(
            text=f"r/{data.get('subreddit', 'unknown')} | 👍 {data.get('ups', 0)}"
        )
        return embed

    @commands.hybrid_command(name="meme", description="Fetch a random meme")
    async def meme(
        self,
        ctx: commands.Context[commands.Bot],
        subreddit: str = "memes",
        nsfw: bool = False,
    ) -> None:
        sub = "nsfw" if nsfw else subreddit
        try:
            async with self.session.get(f"https://meme-api.com/gimme/{sub}") as resp:
                if resp.status == 200:
                    data: dict[str, Any] = await resp.json()
                    embed = self._create_meme_embed(data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a meme.", ephemeral=True)
        except Exception as e:
            logging.error(f"Meme command failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="memes", description="Fetch multiple memes")
    async def memes(
        self,
        ctx: commands.Context[commands.Bot],
        count: int = 5,
        subreddit: str = "memes",
    ) -> None:
        count = min(max(count, 1), 10)
        try:
            async with self.session.get(
                f"https://meme-api.com/gimme/memes/{count * 3}"
            ) as resp:
                if resp.status == 200:
                    response: dict[str, Any] = await resp.json()
                    memes_list = response.get("memes", [])
                    for meme in memes_list[:count]:
                        embed = self._create_meme_embed(meme)
                        await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch memes.", ephemeral=True)
        except Exception as e:
            logging.error(f"Memes command failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="dankmemes", description="Fetch from r/dankmemes")
    async def dankmemes(self, ctx: commands.Context[commands.Bot]) -> None:
        try:
            async with self.session.get("https://meme-api.com/gimme/dankmemes") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = self._create_meme_embed(data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch.", ephemeral=True)
        except Exception as e:
            logging.error(f"Dankmemes failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="me_irl", description="Fetch from r/me_irl")
    async def me_irl(self, ctx: commands.Context[commands.Bot]) -> None:
        try:
            async with self.session.get("https://meme-api.com/gimme/me_irl") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = self._create_meme_embed(data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch.", ephemeral=True)
        except Exception as e:
            logging.error(f"me_irl failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="wholesome", description="Fetch wholesome memes")
    async def wholesome(self, ctx: commands.Context[commands.Bot]) -> None:
        try:
            async with self.session.get(
                "https://meme-api.com/gimme/wholesomememes"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = self._create_meme_embed(data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch.", ephemeral=True)
        except Exception as e:
            logging.error(f"Wholesome failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="memehub", description="Fetch from r/MemeHub")
    async def memehub(self, ctx: commands.Context[commands.Bot]) -> None:
        try:
            async with self.session.get("https://meme-api.com/gimme/MemeHub") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = self._create_meme_embed(data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch.", ephemeral=True)
        except Exception as e:
            logging.error(f"MemeHub failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(
        name="memesub", description="Fetch from a specific subreddit"
    )
    async def memesub(
        self, ctx: commands.Context[commands.Bot], *, subreddit: str
    ) -> None:
        try:
            async with self.session.get(
                f"https://meme-api.com/gimme/{subreddit}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = self._create_meme_embed(data)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(
                        "❌ Failed to fetch. Subreddit may not exist.", ephemeral=True
                    )
        except Exception as e:
            logging.error(f"memesub failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="gif", description="Search for a GIF")
    async def gif(
        self, ctx: commands.Context[commands.Bot], *, query: str = "trending"
    ) -> None:
        klipy_key = os.getenv("KLIPY_API_KEY")
        giphy_key = os.getenv("GIPHY_API_KEY")

        result = None
        provider = ""

        for _ in range(3):
            if klipy_key:
                try:
                    async with self.session.get(
                        "https://api.klipy.com/v1/gifs/search",
                        params={"api_key": klipy_key, "q": query, "limit": 25},
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("data", [])
                            if results:
                                result = random.choice(results)
                                provider = "Klipy"
                                break
                except Exception as e:
                    logging.warning(f"Klipy failed: {e}")

            if not result and giphy_key:
                try:
                    async with self.session.get(
                        "https://api.giphy.com/v1/gifs/search",
                        params={"api_key": giphy_key, "q": query, "limit": 25},
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("data", [])
                            if results:
                                result = random.choice(results)
                                provider = "Giphy"
                                break
                except Exception as e:
                    logging.warning(f"Giphy failed: {e}")

            if not result:
                try:
                    async with self.session.get(
                        "https://tenor.googleapis.com/v2/search",
                        params={
                            "key": "AIzaSyAOESJm3r3tPZQdYfC7J3TqZmHtTqLkqS0",
                            "q": query,
                            "limit": 25,
                        },
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("results", [])
                            if results:
                                result = random.choice(results)
                                provider = "Tenor"
                                break
                except Exception as e:
                    logging.warning(f"Tenor failed: {e}")

        if not result:
            await ctx.send("❌ No GIFs found.", ephemeral=True)
            return

        embed = discord.Embed(
            title=result.get("title", "GIF"), color=discord.Color.random()
        )
        if provider == "Tenor":
            img_url = result.get("media_formats", {}).get("gif")
        elif provider == "Giphy":
            img_url = result.get("images", {}).get("original", {}).get("url")
        else:
            img_url = result.get("url")

        if img_url:
            embed.set_image(url=img_url)
            embed.set_footer(text=f"Source: {provider}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Invalid GIF data.", ephemeral=True)

    @commands.hybrid_command(name="gifs", description="Fetch multiple GIFs")
    async def gifs(
        self,
        ctx: commands.Context[commands.Bot],
        query: str = "trending",
        count: int = 5,
    ) -> None:
        count = min(max(count, 1), 10)
        klipy_key = os.getenv("KLIPY_API_KEY")
        giphy_key = os.getenv("GIPHY_API_KEY")

        gifs_data = []

        if klipy_key:
            try:
                async with self.session.get(
                    "https://api.klipy.com/v1/gifs/search",
                    params={"api_key": klipy_key, "q": query, "limit": count * 2},
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gifs_data = data.get("data", [])
            except Exception as e:
                logging.warning(f"Klipy batch failed: {e}")

        if not gifs_data and giphy_key:
            try:
                async with self.session.get(
                    "https://api.giphy.com/v1/gifs/search",
                    params={"api_key": giphy_key, "q": query, "limit": count * 2},
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gifs_data = data.get("data", [])
            except Exception as e:
                logging.warning(f"Giphy batch failed: {e}")

        if not gifs_data:
            await ctx.send("❌ No GIFs found.", ephemeral=True)
            return

        random.shuffle(gifs_data)
        for gif in gifs_data[:count]:
            embed = discord.Embed(
                title=gif.get("title", "GIF"), color=discord.Color.random()
            )
            img_url = gif.get("images", {}).get("original", {}).get("url")
            if img_url:
                embed.set_image(url=img_url)
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="trending", description="Trending GIFs")
    async def trending(self, ctx: commands.Context[commands.Bot]) -> None:
        giphy_key = os.getenv("GIPHY_API_KEY")

        if not giphy_key:
            await ctx.send("❌ No Giphy key.", ephemeral=True)
            return

        try:
            async with self.session.get(
                "https://api.giphy.com/v1/gifs/trending",
                params={"api_key": giphy_key, "limit": 25},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("data", [])
                    if results:
                        gif = random.choice(results)
                        embed = discord.Embed(
                            title=gif.get("title", "Trending GIF"),
                            color=discord.Color.random(),
                        )
                        img_url = gif.get("images", {}).get("original", {}).get("url")
                        if img_url:
                            embed.set_image(url=img_url)
                            embed.set_footer(text="Source: Giphy Trending")
                            await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch.", ephemeral=True)
        except Exception as e:
            logging.error(f"Trending failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(name="sticker", description="Search for a sticker")
    async def sticker(self, ctx: commands.Context[commands.Bot], *, query: str) -> None:
        giphy_key = os.getenv("GIPHY_API_KEY")

        if not giphy_key:
            await ctx.send("❌ No Giphy key.", ephemeral=True)
            return

        try:
            async with self.session.get(
                "https://api.giphy.com/v1/stickers/search",
                params={"api_key": giphy_key, "q": query, "limit": 25},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("data", [])
                    if results:
                        sticker = random.choice(results)
                        embed = discord.Embed(
                            title=sticker.get("title", "Sticker"),
                            color=discord.Color.random(),
                        )
                        img_url = (
                            sticker.get("images", {}).get("fixed_height", {}).get("url")
                        )
                        if img_url:
                            embed.set_image(url=img_url)
                            embed.set_footer(text="Source: Giphy Stickers")
                            await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ No stickers found.", ephemeral=True)
                else:
                    await ctx.send("❌ Failed to fetch.", ephemeral=True)
        except Exception as e:
            logging.error(f"Sticker failed: {e}")
            await ctx.send("❌ An error occurred.", ephemeral=True)

    @commands.hybrid_command(
        name="random", description="Random command - meme, gif, or subreddit"
    )
    async def random_cmd(
        self,
        ctx: commands.Context[commands.Bot],
        type: str = "meme",
    ) -> None:
        types = ["meme", "gif", "dankmemes", "wholesome", "me_irl", "memehub"]
        if type not in types:
            type = random.choice(types)

        commands_map = {
            "meme": self.meme,
            "gif": self.gif,
            "dankmemes": self.dankmemes,
            "wholesome": self.wholesome,
            "me_irl": self.me_irl,
            "memehub": self.memehub,
        }
        cmd = commands_map.get(type, self.meme)
        await cmd.invoke(ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Memes(bot))
