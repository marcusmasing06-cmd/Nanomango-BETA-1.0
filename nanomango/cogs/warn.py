import discord
from discord.ext import commands
import json
import os

WARN_FILE = "warns.json"


class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(WARN_FILE):
            with open(WARN_FILE, "w") as f:
                json.dump({}, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(WARN_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(WARN_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # WARN COMMAND
    # -----------------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        data = self.load()
        uid = str(member.id)

        if uid not in data:
            data[uid] = []

        data[uid].append({
            "reason": reason,
            "moderator": ctx.author.id
        })

        self.save(data)

        await ctx.send(f"⚠ {member.mention} has been warned — **{reason}**")

        try:
            await member.send(f"⚠ You were warned in **{ctx.guild.name}** — {reason}")
        except:
            pass

    # -----------------------------
    # WARN LIST
    # -----------------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warns(self, ctx, member: discord.Member):
        data = self.load()
        uid = str(member.id)

        if uid not in data or len(data[uid]) == 0:
            return await ctx.send(f"✅ {member.mention} has **no warnings**.")

        embed = discord.Embed(
            title=f"⚠ Warnings for {member.name}",
            color=discord.Color.orange()
        )

        for i, warn in enumerate(data[uid], start=1):
            mod = ctx.guild.get_member(warn["moderator"])
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Reason:** {warn['reason']}\n**Moderator:** {mod.mention if mod else 'Unknown'}",
                inline=False
            )

        await ctx.send(embed=embed)

    # -----------------------------
    # CLEAR WARNINGS
    # -----------------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx, member: discord.Member):
        data = self.load()
        uid = str(member.id)

        if uid not in data or len(data[uid]) == 0:
            return await ctx.send(f"❌ {member.mention} has no warnings to clear.")

        data[uid] = []
        self.save(data)

        await ctx.send(f"🧹 Cleared all warnings for {member.mention}.")


async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
