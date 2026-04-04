import discord
from discord.ext import commands
import aiohttp
import os
import random
import logging
import asyncio

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    @commands.hybrid_command(name="meme", description="Fetch a random meme from Reddit")
    async def meme(self, ctx: commands.Context):
        try:
            async with self.session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(title=data.get("title", "Meme"), color=discord.Color.random())
                    embed.set_image(url=data.get("url"))
                    embed.set_footer(text=f"r/{data.get('subreddit', 'unknown')} | 👍 {data.get('ups', 0)}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a meme. Please try again later.", ephemeral=True)
        except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as e:
            logging.error(f"Meme command failed: {e}")
            await ctx.send("❌ An error occurred while fetching the meme.", ephemeral=True)

    @commands.hybrid_command(name="gif", description="Fetch a random or trending GIF")
    async def gif(self, ctx: commands.Context, *, query: str = "trending"):
        klipy_key = os.getenv("KLIPY_API_KEY")
        giphy_key = os.getenv("GIPHY_API_KEY")
        
        if not klipy_key and not giphy_key:
            await ctx.send("⚠️ No GIF API keys configured.", ephemeral=True)
            return

        async def fetch_klipy():
            if not klipy_key: return None
            try:
                async with self.session.get("https://api.klipy.com/v1/gifs/search", params={"api_key": klipy_key, "q": query, "limit": 10}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("data", [])
                        if results:
                            return random.choice(results), "Klipy"
            except Exception as e:
                logging.warning(f"Klipy request failed: {e}")
            return None

        async def fetch_giphy():
            if not giphy_key: return None
            try:
                async with self.session.get("https://api.giphy.com/v1/gifs/search", params={"api_key": giphy_key, "q": query, "limit": 10}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
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
            embed = discord.Embed(title=gif_data.get("title", "GIF"), color=discord.Color.random())
            img_url = gif_data.get("url") or gif_data.get("images", {}).get("original", {}).get("url")
            if img_url:
                embed.set_image(url=img_url)
                embed.set_footer(text=f"Source: {provider}")
                await ctx.send(embed=embed)
                logging.info(f"GIF fetched via {provider}")
            else:
                await ctx.send("❌ Received invalid GIF data from provider.", ephemeral=True)
        else:
            await ctx.send("Sorry, I couldn't find any GIFs right now. Please try again later!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Memes(bot))
