import discord
from discord.ext import commands
import json
import os
import time

ANTIRAID_FILE = "antiraid.json"


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create config if missing
        if not os.path.exists(ANTIRAID_FILE):
            with open(ANTIRAID_FILE, "w") as f:
                json.dump({
                    "enabled": False,
                    "join_limit": 5,          # joins per interval
                    "interval": 10,           # seconds
                    "lockdown_role": None,    # optional
                    "alert_channel": None
                }, f, indent=4)

        # Track joins
        self.join_times = []

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(ANTIRAID_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(ANTIRAID_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def antiraid(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Commands: `on`, `off`, `status`, `settings`, `alert`")

    @antiraid.command()
    async def on(self, ctx):
        data = self.load()
        data["enabled"] = True
        self.save(data)
        await ctx.send("🛡 Anti‑Raid system **enabled**.")

    @antiraid.command()
    async def off(self, ctx):
        data = self.load()
        data["enabled"] = False
        self.save(data)
        await ctx.send("❌ Anti‑Raid system **disabled**.")

    @antiraid.command()
    async def status(self, ctx):
        data = self.load()
        enabled = data["enabled"]
        await ctx.send(f"Anti‑Raid is **{'ON' if enabled else 'OFF'}**.")

    @antiraid.command()
    async def settings(self, ctx):
        data = self.load()
        embed = discord.Embed(
            title="🛡 Anti‑Raid Settings",
            color=discord.Color.red()
        )
        embed.add_field(name="Enabled", value=str(data["enabled"]))
        embed.add_field(name="Join Limit", value=str(data["join_limit"]))
        embed.add_field(name="Interval (seconds)", value=str(data["interval"]))
        embed.add_field(name="Alert Channel", value=str(data["alert_channel"]))
        await ctx.send(embed=embed)

    @antiraid.command()
    async def alert(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["alert_channel"] = channel.id
        self.save(data)
        await ctx.send(f"📢 Alerts will be sent to {channel.mention}")

    # -----------------------------
    # Raid Detection
    # -----------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = self.load()
        if not data["enabled"]:
            return

        now = time.time()
        self.join_times.append(now)

        # Remove old timestamps
        self.join_times = [t for t in self.join_times if now - t <= data["interval"]]

        # Check threshold
        if len(self.join_times) >= data["join_limit"]:
            await self.trigger_lockdown(member.guild)

    # -----------------------------
    # Lockdown
    # -----------------------------
    async def trigger_lockdown(self, guild):
        data = self.load()

        # Slowmode all channels
        for channel in guild.text_channels:
            try:
                await channel.edit(slowmode_delay=10)
            except:
                pass

        # Alert staff
        if data["alert_channel"]:
            channel = guild.get_channel(data["alert_channel"])
            if channel:
                await channel.send("🚨 **RAID DETECTED!** Server is in lockdown mode.")

        # Reset join tracking
        self.join_times = []


async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
