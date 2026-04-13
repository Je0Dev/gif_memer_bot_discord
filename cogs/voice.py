import logging
import random
from typing import Optional

import discord
from discord import FFmpegPCMAudio
from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.voice_clients: dict[int, discord.VoiceClient] = {}

    @commands.hybrid_command(name="join", description="Join voice channel")
    async def join(self, ctx: commands.Context[commands.Bot]) -> None:
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!", ephemeral=True)
            return

        channel = ctx.author.voice.channel
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.move_to(channel)
        else:
            vc = await channel.connect()
            self.voice_clients[ctx.guild.id] = vc
        await ctx.send(f"✅ Joined {channel.name}")

    @commands.hybrid_command(name="leave", description="Leave voice channel")
    async def leave(self, ctx: commands.Context[commands.Bot]) -> None:
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send("✅ Left voice channel")
        else:
            await ctx.send("❌ Not in a voice channel!", ephemeral=True)

    @commands.hybrid_command(name="play", description="Play audio from URL")
    async def play(self, ctx: commands.Context[commands.Bot], *, url: str) -> None:
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!", ephemeral=True)
            return

        if not ctx.guild.voice_client:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            self.voice_clients[ctx.guild.id] = vc

        try:
            source = FFmpegPCMAudio(url)
            ctx.guild.voice_client.play(source)
            await ctx.send(f"▶️ Playing: {url}")
        except Exception as e:
            logging.error(f"Play failed: {e}")
            await ctx.send("❌ Failed to play audio", ephemeral=True)

    @commands.hybrid_command(name="pause", description="Pause current audio")
    async def pause(self, ctx: commands.Context[commands.Bot]) -> None:
        if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.pause()
            await ctx.send("⏸️ Paused")
        else:
            await ctx.send("❌ Not playing anything!", ephemeral=True)

    @commands.hybrid_command(name="resume", description="Resume paused audio")
    async def resume(self, ctx: commands.Context[commands.Bot]) -> None:
        if ctx.guild.voice_client and ctx.guild.voice_client.is_paused():
            ctx.guild.voice_client.resume()
            await ctx.send("▶️ Resumed")
        else:
            await ctx.send("❌ Nothing paused!", ephemeral=True)

    @commands.hybrid_command(name="stop", description="Stop current audio")
    async def stop(self, ctx: commands.Context[commands.Bot]) -> None:
        if ctx.guild.voice_client:
            ctx.guild.voice_client.stop()
            await ctx.send("⏹️ Stopped")
        else:
            await ctx.send("❌ Not playing anything!", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Voice(bot))
