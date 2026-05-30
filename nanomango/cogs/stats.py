import discord
from discord.ext import commands, tasks
import json
import os

STATS_FILE = "stats.json"


class StatsSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create config if missing
        if not os.path.exists(STATS_FILE):
            with open(STATS_FILE, "w") as f:
                json.dump({
                    "enabled": False,
                    "channels": {
                        "members": None,
                        "online": None,
                        "boosts": None
                    }
                }, f, indent=4)

        self.update_stats.start()

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(STATS_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(STATS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setstats(self, ctx):
        """Creates the 3 stat channels."""
        data = self.load()

        if data["enabled"]:
            return await ctx.send("📊 Stats are already set up.")

        guild = ctx.guild

        members_ch = await guild.create_voice_channel("👥 Members: 0")
        online_ch = await guild.create_voice_channel("🟢 Online: 0")
        boosts_ch = await guild.create_voice_channel("🎮 Boosts: 0")

        data["channels"]["members"] = members_ch.id
        data["channels"]["online"] = online_ch.id
        data["channels"]["boosts"] = boosts_ch.id
        data["enabled"] = True

        self.save(data)

        await ctx.send("📊 Stats channels created.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def statsreset(self, ctx):
        """Deletes and recreates the stat channels."""
        data = self.load()
        guild = ctx.guild

        for ch_id in data["channels"].values():
            if ch_id:
                ch = guild.get_channel(ch_id)
                if ch:
                    await ch.delete()

        data["enabled"] = False
        data["channels"] = {"members": None, "online": None, "boosts": None}
        self.save(data)

        await ctx.send("♻ Stats reset. Use `!setstats` to recreate them.")

    @commands.command()
    async def statsstatus(self, ctx):
        data = self.load()
        if not data["enabled"]:
            return await ctx.send("❌ Stats system is **not** enabled.")

        await ctx.send("📊 Stats system is **active**.")

    # -----------------------------
    # Auto Update
    # -----------------------------
    @tasks.loop(minutes=5)
    async def update_stats(self):
        data = self.load()
        if not data["enabled"]:
            return

        for guild in self.bot.guilds:
            await self.update_guild_stats(guild, data)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = self.load()
        if data["enabled"]:
            await self.update_guild_stats(member.guild, data)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = self.load()
        if data["enabled"]:
            await self.update_guild_stats(member.guild, data)

    # -----------------------------
    # Update Logic
    # -----------------------------
    async def update_guild_stats(self, guild, data):
        members = guild.member_count
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)
        boosts = guild.premium_subscription_count

        ch_members = guild.get_channel(data["channels"]["members"])
        ch_online = guild.get_channel(data["channels"]["online"])
        ch_boosts = guild.get_channel(data["channels"]["boosts"])

        if ch_members:
            await ch_members.edit(name=f"👥 Members: {members}")
        if ch_online:
            await ch_online.edit(name=f"🟢 Online: {online}")
        if ch_boosts:
            await ch_boosts.edit(name=f"🎮 Boosts: {boosts}")


async def setup(bot):
    await bot.add_cog(StatsSystem(bot))
