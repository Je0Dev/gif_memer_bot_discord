import discord
from discord.ext import commands
import aiohttp
import os
import random

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tenor_key = os.getenv("TENOR_API_KEY")

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
        if not self.tenor_key:
            await ctx.send("⚠️ Tenor API key is not configured.")
            return

        url = f"https://g.tenor.com/v1/search?q={query}&key={self.tenor_key}&limit=10"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["results"]:
                        gif = random.choice(data["results"])
                        embed = discord.Embed(title=gif["title"], color=discord.Color.random())
                        embed.set_image(url=gif["media"][0]["gif"]["url"])
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("🔍 No GIFs found for that query.")
                else:
                    await ctx.send("❌ Failed to fetch GIF. Please check the API key or try again.")

async def setup(bot):
    await bot.add_cog(Memes(bot))
