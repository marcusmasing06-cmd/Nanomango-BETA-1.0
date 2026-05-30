import discord
from discord.ext import commands
import json
import os

SUGGEST_FILE = "suggestions.json"


class SuggestionSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(SUGGEST_FILE):
            with open(SUGGEST_FILE, "w") as f:
                json.dump({
                    "channel": None,
                    "suggestions": {}
                }, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(SUGGEST_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(SUGGEST_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Set suggestion channel
    # -----------------------------
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setsuggest(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["channel"] = channel.id
        self.save(data)
        await ctx.send(f"💡 Suggestions will now go to {channel.mention}")

    # -----------------------------
    # Suggest command
    # -----------------------------
    @commands.command()
    async def suggest(self, ctx, *, text: str):
        data = self.load()
        ch_id = data["channel"]

        if not ch_id:
            return await ctx.send("❌ Suggestions are not set up.")

        channel = ctx.guild.get_channel(ch_id)
        if not channel:
            return await ctx.send("❌ Suggestion channel is missing.")

        embed = discord.Embed(
            title="💡 New Suggestion",
            description=text,
            color=discord.Color.yellow()
        )
        embed.set_footer(text=f"Suggested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        msg = await channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        # Save suggestion
        data["suggestions"][str(msg.id)] = {
            "author": ctx.author.id,
            "text": text
        }
        self.save(data)

        await ctx.send("✅ Your suggestion has been submitted!")

    # -----------------------------
    # View suggestion info
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def suggestinfo(self, ctx, message_id: int):
        data = self.load()

        if str(message_id) not in data["suggestions"]:
            return await ctx.send("❌ Suggestion not found.")

        sug = data["suggestions"][str(message_id)]
        user = ctx.guild.get_member(sug["author"])

        embed = discord.Embed(
            title="💡 Suggestion Info",
            color=discord.Color.blue()
        )
        embed.add_field(name="Author", value=user.mention if user else "Unknown")
        embed.add_field(name="Content", value=sug["text"], inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SuggestionSystem(bot))
