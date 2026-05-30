import discord
from discord.ext import commands
import json
import os
import aiofiles

WARN_FILE = "warnings.json"

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(WARN_FILE):
            with open(WARN_FILE, "w") as f:
                json.dump({}, f)

    # -----------------------------
    # Load & Save warnings
    # -----------------------------
    async def load_warnings(self):
        async with aiofiles.open(WARN_FILE, "r") as f:
            data = await f.read()
            return json.loads(data)

    async def save_warnings(self, data):
        async with aiofiles.open(WARN_FILE, "w") as f:
            await f.write(json.dumps(data, indent=4))

    # -----------------------------
    # Kick
    # -----------------------------
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 Kicked **{member}** — {reason}")

    # -----------------------------
    # Ban
    # -----------------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 Banned **{member}** — {reason}")

    # -----------------------------
    # Unban
    # -----------------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, username):
        banned = await ctx.guild.bans()
        name, discrim = username.split("#")

        for ban_entry in banned:
            user = ban_entry.user
            if (user.name, user.discriminator) == (name, discrim):
                await ctx.guild.unban(user)
                return await ctx.send(f"♻️ Unbanned **{user}**")

        await ctx.send("User not found in ban list.")

    # -----------------------------
    # Clear messages
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Cleared **{amount}** messages.", delete_after=3)

    # -----------------------------
    # Timeout (mute)
    # -----------------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"🔇 Muted **{member}** for **{minutes} minutes** — {reason}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 Unmuted **{member}**")

# -----------------------------
# Setup
# -----------------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))
