import discord
from discord.ext import commands
import aiohttp
import os
import random
import logging

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="meme", description="Fetch a random meme from Reddit")
    async def meme(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(title=data["title"], color=discord.Color.random())
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"r/{data['subreddit']} | 👍 {data['ups']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a meme. Please try again later.")

    @commands.hybrid_command(name="gif", description="Fetch a random or trending GIF")
    async def gif(self, ctx: commands.Context, *, query: str = "trending"):
        klipy_key = os.getenv("KLIPY_API_KEY")
        giphy_key = os.getenv("GIPHY_API_KEY")
        
        if not klipy_key and not giphy_key:
            await ctx.send("⚠️ No GIF API keys configured.", ephemeral=True)
            return

        async with aiohttp.ClientSession() as session:
            # Try Klipy first
            if klipy_key:
                try:
                    klipy_url = "https://api.klipy.com/v1/gifs/search"
                    async with session.get(klipy_url, params={"api_key": klipy_key, "q": query, "limit": 10}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("data", [])
                            if results:
                                gif = random.choice(results)
                                embed = discord.Embed(title=gif.get("title", "GIF"), color=discord.Color.random())
                                img_url = gif.get("url") or gif.get("images", {}).get("original", {}).get("url")
                                if img_url:
                                    embed.set_image(url=img_url)
                                    embed.set_footer(text="Source: Klipy")
                                    await ctx.send(embed=embed)
                                    logging.info("GIF fetched via Klipy")
                                    return
                        logging.info(f"Klipy failed or returned no results (Status: {resp.status}), falling back to Giphy")
                except Exception as e:
                    logging.info(f"Klipy request failed: {e}, falling back to Giphy")

            # Try Giphy
            if giphy_key:
                try:
                    giphy_url = "https://api.giphy.com/v1/gifs/search"
                    async with session.get(giphy_url, params={"api_key": giphy_key, "q": query, "limit": 10}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get("data", [])
                            if results:
                                gif = random.choice(results)
                                embed = discord.Embed(title=gif.get("title", "GIF"), color=discord.Color.random())
                                img_url = gif.get("images", {}).get("original", {}).get("url")
                                if img_url:
                                    embed.set_image(url=img_url)
                                    embed.set_footer(text="Source: Giphy")
                                    await ctx.send(embed=embed)
                                    logging.info("GIF fetched via Giphy")
                                    return
                        logging.info(f"Giphy failed or returned no results (Status: {resp.status})")
                except Exception as e:
                    logging.info(f"Giphy request failed: {e}")

            await ctx.send("Sorry, I couldn't find any GIFs right now. Please try again later!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Memes(bot))
