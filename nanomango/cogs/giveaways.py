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
    # Start Giveaway (smooth countdown)
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def gstart(self, ctx, time: str, *, prize: str):
        seconds = self.parse_time(time)
        if seconds is None:
            return await ctx.send("❌ Invalid time format. Use: `10s`, `5m`, `2h`, `3d`")

        end_time = asyncio.get_event_loop().time() + seconds

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

        # -----------------------------
        # COUNTDOWN LOOP
        # -----------------------------
        last_display = None

        while True:
            remaining = int(end_time - asyncio.get_event_loop().time())

            if remaining <= 0:
                break

            # Only update when the number changes (prevents rate limits)
            if remaining != last_display:
                last_display = remaining

                embed.description = (
                    f"**Prize:** {prize}\n"
                    f"**Host:** {ctx.author.mention}\n"
                    f"**Ends in:** `{remaining}s`\n\n"
                    f"React with 🎉 to enter!"
                )

                try:
                    await msg.edit(embed=embed)
                except:
                    pass  # ignore edit failures safely

            await asyncio.sleep(0.25)  # smooth updates without spamming

        # -----------------------------
        # PICK WINNER
        # -----------------------------
        msg = await ctx.channel.fetch_message(msg.id)
        reaction = discord.utils.get(msg.reactions, emoji="🎉")

        if not reaction:
            return await ctx.send("❌ No one reacted.")

        users = await reaction.users().flatten()

        # Remove bot
        if ctx.guild.me in users:
            users.remove(ctx.guild.me)

        if len(users) == 0:
            return await ctx.send("❌ No valid entries. Giveaway cancelled.")

        winner = random.choice(users)

        await ctx.send(f"🎉 **Giveaway Ended!** Winner of **{prize}**: {winner.mention}")

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
