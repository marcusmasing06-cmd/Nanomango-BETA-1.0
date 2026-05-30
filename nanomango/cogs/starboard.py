import discord
from discord.ext import commands
import json
import os

STARBOARD_FILE = "starboard.json"


class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(STARBOARD_FILE):
            with open(STARBOARD_FILE, "w") as f:
                json.dump({
                    "channel": None,
                    "emoji": "⭐",
                    "limit": 3,
                    "posted": []
                }, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(STARBOARD_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(STARBOARD_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Starboard Commands
    # -----------------------------
    @commands.group()
    @commands.has_permissions(manage_messages=True)
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Commands: `setchannel`, `setemoji`, `setlimit`")

    @starboard.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["channel"] = channel.id
        self.save(data)
        await ctx.send(f"🌟 Starboard channel set to {channel.mention}")

    @starboard.command()
    async def setemoji(self, ctx, emoji: str):
        data = self.load()
        data["emoji"] = emoji
        self.save(data)
        await ctx.send(f"🌟 Starboard emoji set to `{emoji}`")

    @starboard.command()
    async def setlimit(self, ctx, number: int):
        data = self.load()
        data["limit"] = number
        self.save(data)
        await ctx.send(f"🌟 Starboard limit set to `{number}` reactions")

    # -----------------------------
    # Reaction Listener
    # -----------------------------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        data = self.load()

        # Starboard not set up
        if data["channel"] is None:
            return

        # Wrong emoji
        if str(payload.emoji) != data["emoji"]:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Count reactions
        for reaction in message.reactions:
            if str(reaction.emoji) == data["emoji"]:
                count = reaction.count
                break
        else:
            return

        # Not enough reactions yet
        if count < data["limit"]:
            return

        # Already posted
        if message.id in data["posted"]:
            return

        # Mark as posted
        data["posted"].append(message.id)
        self.save(data)

        # Starboard channel
        starboard_channel = message.guild.get_channel(data["channel"])
        if not starboard_channel:
            return

        # Build embed
        embed = discord.Embed(
            title="🌟 Starred Message",
            description=message.content or "*No text content*",
            color=discord.Color.gold()
        )

        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Stars", value=str(count), inline=True)
        embed.add_field(
            name="Jump to Message",
            value=f"[Click Here]({message.jump_url})",
            inline=False
        )

        # Attach image if exists
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await starboard_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Starboard(bot))
