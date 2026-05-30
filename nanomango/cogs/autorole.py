import discord
from discord.ext import commands
import json
import os

AUTOROLE_FILE = "autorole.json"


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(AUTOROLE_FILE):
            with open(AUTOROLE_FILE, "w") as f:
                json.dump({
                    "role_id": None,
                    "log_channel": None,
                    "enabled": False
                }, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(AUTOROLE_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(AUTOROLE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.group()
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Commands: `set`, `off`, `status`, `log`")

    @autorole.command()
    async def set(self, ctx, role: discord.Role):
        data = self.load()
        data["role_id"] = role.id
        data["enabled"] = True
        self.save(data)

        await ctx.send(f"✅ Auto‑role enabled. New members will receive **{role.name}**")

    @autorole.command()
    async def off(self, ctx):
        data = self.load()
        data["enabled"] = False
        self.save(data)

        await ctx.send("❌ Auto‑role disabled.")

    @autorole.command()
    async def status(self, ctx):
        data = self.load()
        role_id = data["role_id"]
        enabled = data["enabled"]

        if not enabled or role_id is None:
            return await ctx.send("⚠ Auto‑role is **disabled**.")

        role = ctx.guild.get_role(role_id)
        await ctx.send(f"✅ Auto‑role is **enabled**.\nRole: **{role.name}**")

    @autorole.command()
    async def log(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["log_channel"] = channel.id
        self.save(data)

        await ctx.send(f"📒 Auto‑role logs will go to {channel.mention}")

    # -----------------------------
    # Member Join Event
    # -----------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = self.load()

        if not data["enabled"]:
            return

        role_id = data["role_id"]
        if role_id is None:
            return

        role = member.guild.get_role(role_id)
        if role is None:
            return

        try:
            await member.add_roles(role, reason="Auto‑role system")
        except:
            return

        # Logging
        log_channel_id = data.get("log_channel")
        if log_channel_id:
            channel = member.guild.get_channel(log_channel_id)
            if channel:
                await channel.send(f"👤 Gave **{role.name}** to {member.mention}")


async def setup(bot):
    await bot.add_cog(AutoRole(bot))
