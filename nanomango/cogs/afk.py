import discord
from discord.ext import commands

class AFK(commands.Cog):
    """AFK system for NanoMango."""

    def __init__(self, bot):
        self.bot = bot
        self.afk = {}  # {user_id: reason}

    @commands.command()
    async def afk(self, ctx, *, reason="AFK"):
        """Set yourself as AFK."""
        self.afk[ctx.author.id] = reason
        await ctx.send(f"{ctx.author.mention} is now AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Prevent instant "welcome back" when typing !afk
        if message.content.startswith("!afk"):
            return

        # Remove AFK when user speaks
        if message.author.id in self.afk:
            self.afk.pop(message.author.id)
            await message.channel.send(f"{message.author.mention}, welcome back")

        # Notify when mentioning AFK users
        if message.mentions:
            for user in message.mentions:
                if user.id in self.afk:
                    await message.channel.send(
                        f"{user.name} is AFK: {self.afk[user.id]}"
                    )

async def setup(bot):
    await bot.add_cog(AFK(bot))
