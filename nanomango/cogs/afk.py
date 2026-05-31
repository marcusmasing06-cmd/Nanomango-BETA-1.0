import discord
from discord.ext import commands

class AFK(commands.Cog):
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
        # Ignore bot messages
        if message.author.bot:
            return

        # Ignore AFK command itself so it doesn't instantly remove AFK
        if message.content.startswith("!afk"):
            return

        # If user was AFK and sends a message → remove AFK
        if message.author.id in self.afk:
            del self.afk[message.author.id]
            await message.channel.send(f"{message.author.mention}, welcome back")

        # If someone mentions an AFK user → notify
        if message.mentions:
            for user in message.mentions:
                if user.id in self.afk:
                    reason = self.afk[user.id]
                    await message.channel.send(f"{user.name} is AFK: {reason}")

        # Process commands AFTER AFK logic
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(AFK(bot))
