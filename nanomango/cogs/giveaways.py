import discord
from discord.ext import commands
import asyncio
import random
import re


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------
    # Time Parser
    # -----------------------------
    def parse_time(self, time_str):
        match = re.match(r"(\d+)(s|m|h|d)$", time_str)
        if not match:
            return None

        value, unit = match.groups()
        value = int(value)

        if unit == "s":
            return value
        if unit == "m":
            return value * 60
        if unit == "h":
            return value * 3600
        if unit == "d":
            return value * 86400

        return None

    # -----------------------------
    # Start Giveaway
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def gstart(self, ctx, time: str, *, prize: str):
        seconds = self.parse_time(time)
        if seconds is None:
            return await ctx.send("❌ Invalid time format. Use: `10s`, `5m`, `2h`, `3d`")

        embed = discord.Embed(
            title="🎉 Giveaway Started!",
            description=f"**Prize:** {prize}\n"
                        f"**Host:** {ctx.author.mention}\n"
                        f"**Ends in:** `{time}`\n\n"
                        f"React with 🎉 to enter!",
            color=discord.Color.green()
        )

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        await asyncio.sleep(seconds)

        # Fetch updated message
        msg = await ctx.channel.fetch_message(msg.id)
        users = await msg.reactions[0].users().flatten()

        # Remove bot from entries
        if ctx.guild.me in users:
            users.remove(ctx.guild.me)

        if len(users) == 0:
            return await ctx.send("❌ No valid entries. Giveaway cancelled.")

        winner = random.choice(users)

        await ctx.send(f"🎉 **Giveaway Ended!**\nWinner of **{prize}**: {winner.mention}")

    # -----------------------------
    # End Giveaway Early
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def gend(self, ctx, message_id: int):
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except:
            return await ctx.send("❌ Invalid message ID.")

        if not msg.embeds:
            return await ctx.send("❌ That message is not a giveaway.")

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        if not reaction:
            return await ctx.send("❌ No 🎉 reaction found on that message.")

        users = await reaction.users().flatten()
        if ctx.guild.me in users:
            users.remove(ctx.guild.me)

        if len(users) == 0:
            return await ctx.send("❌ No valid entries.")

        winner = random.choice(users)
        await ctx.send(f"🎉 **Giveaway Ended Early!** Winner: {winner.mention}")

    # -----------------------------
    # Reroll Giveaway
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def greroll(self, ctx, message_id: int):
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except:
            return await ctx.send("❌ Invalid message ID.")

        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        if not reaction:
            return await ctx.send("❌ No 🎉 reaction found on that message.")

        users = await reaction.users().flatten()
        if ctx.guild.me in users:
            users.remove(ctx.guild.me)

        if len(users) == 0:
            return await ctx.send("❌ No valid entries.")

        winner = random.choice(users)
        await ctx.send(f"🔄 **Rerolled!** New winner: {winner.mention}")


async def setup(bot):
    await bot.add_cog(Giveaways(bot))
