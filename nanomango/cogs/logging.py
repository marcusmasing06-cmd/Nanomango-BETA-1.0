import discord
from discord.ext import commands
import json
import os

LOG_FILE = "logging_config.json"


class LoggingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create config if missing
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump({"log_channel": None}, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(LOG_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["log_channel"] = channel.id
        self.save(data)
        await ctx.send(f"📜 Logging channel set to {channel.mention}")

    @commands.command()
    async def logstatus(self, ctx):
        data = self.load()
        ch = data["log_channel"]
        if ch is None:
            return await ctx.send("❌ Logging is **not** set up.")
        channel = ctx.guild.get_channel(ch)
        await ctx.send(f"📜 Logging is active in {channel.mention}")

    # -----------------------------
    # Helper
    # -----------------------------
    async def send_log(self, guild, embed):
        data = self.load()
        ch_id = data["log_channel"]
        if not ch_id:
            return
        channel = guild.get_channel(ch_id)
        if channel:
            await channel.send(embed=embed)

    # -----------------------------
    # Events
    # -----------------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return

        embed = discord.Embed(
            title="🗑 Message Deleted",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=message.author.mention)
        embed.add_field(name="Channel", value=message.channel.mention)
        embed.add_field(name="Content", value=message.content or "None", inline=False)

        await self.send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author.bot:
            return
        if before.content == after.content:
            return

        embed = discord.Embed(
            title="✏ Message Edited",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=before.author.mention)
        embed.add_field(name="Channel", value=before.channel.mention)
        embed.add_field(name="Before", value=before.content or "None", inline=False)
        embed.add_field(name="After", value=after.content or "None", inline=False)

        await self.send_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green()
        )
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="📤 Member Left",
            description=f"{member.mention} left the server.",
            color=discord.Color.red()
        )
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                title="📝 Nickname Changed",
                color=discord.Color.blue()
            )
            embed.add_field(name="User", value=after.mention)
            embed.add_field(name="Before", value=before.nick or "None")
            embed.add_field(name="After", value=after.nick or "None")
            await self.send_log(after.guild, embed)

        if before.roles != after.roles:
            embed = discord.Embed(
                title="🎭 Roles Updated",
                color=discord.Color.purple()
            )
            embed.add_field(name="User", value=after.mention)
            embed.add_field(
                name="Roles",
                value=", ".join([r.mention for r in after.roles if r.name != "@everyone"])
                or "None",
                inline=False
            )
            await self.send_log(after.guild, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"{user} was banned.",
            color=discord.Color.dark_red()
        )
        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title="⚖ Member Unbanned",
            description=f"{user} was unbanned.",
            color=discord.Color.green()
        )
        await self.send_log(guild, embed)


async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))
