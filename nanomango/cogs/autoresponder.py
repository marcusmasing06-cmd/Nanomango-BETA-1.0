import discord
from discord.ext import commands
import json
import os

AUTORESP_FILE = "autorespond.json"


class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(AUTORESP_FILE):
            with open(AUTORESP_FILE, "w") as f:
                json.dump({"responses": {}}, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(AUTORESP_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(AUTORESP_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Add auto-response
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def addresponse(self, ctx, trigger: str, *, reply: str):
        data = self.load()

        data["responses"][trigger.lower()] = reply
        self.save(data)

        await ctx.send(f"🤖 Added auto-response for trigger: **{trigger}**")

    # -----------------------------
    # Remove auto-response
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delresponse(self, ctx, trigger: str):
        data = self.load()

        if trigger.lower() not in data["responses"]:
            return await ctx.send("❌ That trigger does not exist.")

        del data["responses"][trigger.lower()]
        self.save(data)

        await ctx.send(f"🗑 Removed auto-response for **{trigger}**")

    # -----------------------------
    # List responses
    # -----------------------------
    @commands.command()
    async def responses(self, ctx):
        data = self.load()
        res = data["responses"]

        if not res:
            return await ctx.send("📭 No auto-responses set.")

        embed = discord.Embed(
            title="🤖 Auto-Responses",
            color=discord.Color.blue()
        )

        for trigger, reply in res.items():
            embed.add_field(name=trigger, value=reply, inline=False)

        await ctx.send(embed=embed)

    # -----------------------------
    # Listener
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = self.load()
        content = message.content.lower()

        for trigger, reply in data["responses"].items():
            if trigger in content:
                await message.channel.send(reply)
                break



async def setup(bot):
    await bot.add_cog(AutoResponder(bot))
