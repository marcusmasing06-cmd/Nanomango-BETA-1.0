import discord
from discord.ext import commands
import json
import os

WELCOME_FILE = "welcome.json"


class WelcomeSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create config if missing
        if not os.path.exists(WELCOME_FILE):
            with open(WELCOME_FILE, "w") as f:
                json.dump({
                    "channel": None,
                    "message": "Welcome to the server, {user}!"
                }, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(WELCOME_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(WELCOME_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["channel"] = channel.id
        self.save(data)
        await ctx.send(f"👋 Welcome messages will now be sent in {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcomemsg(self, ctx, *, text: str):
        data = self.load()
        data["message"] = text
        self.save(data)
        await ctx.send("✏ Welcome message updated.")

    @commands.command()
    async def welcomestatus(self, ctx):
        data = self.load()
        ch = data["channel"]
        msg = data["message"]

        if not ch:
            return await ctx.send("❌ Welcome system is **not** set up.")

        channel = ctx.guild.get_channel(ch)
        await ctx.send(
            f"👋 Welcome system is active.\n"
            f"Channel: {channel.mention}\n"
            f"Message: `{msg}`"
        )

    # -----------------------------
    # Event
    # -----------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = self.load()
        ch_id = data["channel"]
        if not ch_id:
            return

        channel = member.guild.get_channel(ch_id)
        if not channel:
            return

        msg = data["message"].replace("{user}", member.mention)

        embed = discord.Embed(
            title="👋 Welcome!",
            description=msg,
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WelcomeSystem(bot))
