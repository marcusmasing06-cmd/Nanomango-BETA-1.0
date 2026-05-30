import discord
from discord.ext import commands
import json
import os
import time

AFK_FILE = "afk.json"


class AFKSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(AFK_FILE):
            with open(AFK_FILE, "w") as f:
                json.dump({}, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(AFK_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(AFK_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Set AFK
    # -----------------------------
    @commands.command()
    async def afk(self, ctx, *, reason="AFK"):
        user_id = str(ctx.author.id)
        data = self.load()

        data[user_id] = {
            "reason": reason,
            "time": int(time.time())
        }

        self.save(data)

        await ctx.send(f"💤 {ctx.author.mention} is now AFK — **{reason}**")

    # -----------------------------
    # Remove AFK on message
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        data = self.load()

        # If user was AFK, remove it
        if user_id in data:
            del data[user_id]
            self.save(data)
            await message.channel.send(f"👋 Welcome back, {message.author.mention}. AFK removed.")

        # Check mentions
        if message.mentions:
            for user in message.mentions:
                uid = str(user.id)
                if uid in data:
                    reason = data[uid]["reason"]
                    await message.channel.send(
                        f"💤 {user.mention} is AFK — **{reason}**"
                    )


async def setup(bot):
    await bot.add_cog(AFKSystem(bot))
