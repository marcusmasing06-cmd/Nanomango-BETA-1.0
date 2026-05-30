import discord
from discord.ext import commands
import json
import re
import time
import os

AUTOMOD_FILE = "automod.json"


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(AUTOMOD_FILE):
            with open(AUTOMOD_FILE, "w") as f:
                json.dump({
                    "enabled": True,
                    "bad_words": [],
                    "log_channel": None,

                    # Feature toggles
                    "features": {
                        "anti_spam": True,
                        "anti_link": True,
                        "anti_ghostping": True,
                        "anti_massmention": True,
                        "anti_emojispam": True,
                        "anti_caps": True,
                        "anti_attachmentspam": True,
                        "auto_slowmode": True
                    },

                    # Limits
                    "limits": {
                        "massmention": 5,
                        "emojis": 10,
                        "caps": 20,
                        "attachments": 4
                    },

                    # Strike system
                    "strike_limits": {
                        "mute": 3,
                        "kick": 5,
                        "ban": 7
                    },

                    "strikes": {}
                }, f, indent=4)

        self.cooldowns = {}  # anti-spam
        self.attachment_tracker = {}  # anti-attachment spam

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(AUTOMOD_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(AUTOMOD_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Config Commands
    # -----------------------------
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Commands: `on/off`, `addword`, `removeword`, `toggle`, `setlimit`, `log`, `settings`")

    @automod.command()
    async def settings(self, ctx):
        data = self.load()
        features = data["features"]
        limits = data["limits"]

        embed = discord.Embed(title="⚙️ AutoMod Settings", color=discord.Color.yellow())

        embed.add_field(
            name="Features",
            value="\n".join([f"**{k}**: {'ON' if v else 'OFF'}" for k, v in features.items()]),
            inline=False
        )

        embed.add_field(
            name="Limits",
            value="\n".join([f"**{k}**: {v}" for k, v in limits.items()]),
            inline=False
        )

        await ctx.send(embed=embed)

    @automod.command()
    async def toggle(self, ctx, feature):
        data = self.load()

        if feature not in data["features"]:
            return await ctx.send("❌ Unknown feature.")

        data["features"][feature] = not data["features"][feature]
        self.save(data)

        await ctx.send(f"🔧 `{feature}` is now **{'ON' if data['features'][feature] else 'OFF'}**")

    @automod.command()
    async def setlimit(self, ctx, feature, number: int):
        data = self.load()

        if feature not in data["limits"]:
            return await ctx.send("❌ Unknown limit.")

        data["limits"][feature] = number
        self.save(data)

        await ctx.send(f"📏 `{feature}` limit set to **{number}**")

    @automod.command()
    async def addword(self, ctx, *, word):
        data = self.load()
        data["bad_words"].append(word.lower())
        self.save(data)
        await ctx.send(f"🔧 Added filtered word: `{word}`")

    @automod.command()
    async def removeword(self, ctx, *, word):
        data = self.load()
        if word.lower() in data["bad_words"]:
            data["bad_words"].remove(word.lower())
            self.save(data)
            await ctx.send(f"🗑 Removed filtered word: `{word}`")
        else:
            await ctx.send("That word is not in the filter list.")

    @automod.command()
    async def log(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["log_channel"] = channel.id
        self.save(data)
        await ctx.send(f"📒 AutoMod logs will go to {channel.mention}")

    # -----------------------------
    # Logging Helper
    # -----------------------------
    async def log_action(self, guild, message):
        data = self.load()
        channel_id = data.get("log_channel")
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.send(message)

    # -----------------------------
    # Strike System
    # -----------------------------
    def add_strike(self, user_id):
        data = self.load()
        strikes = data["strikes"].get(str(user_id), 0) + 1
        data["strikes"][str(user_id)] = strikes
        self.save(data)
        return strikes

    # -----------------------------
    # AutoMod Event
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = self.load()
        features = data["features"]
        limits = data["limits"]

        # Admin bypass
        if message.author.guild_permissions.manage_messages:
            return

        content = message.content.lower()
        user_id = message.author.id
        guild = message.guild

        # -----------------------------
        # Anti-Spam
        # -----------------------------
        if features["anti_spam"]:
            now = time.time()
            self.cooldowns.setdefault(user_id, []).append(now)
            self.cooldowns[user_id] = [t for t in self.cooldowns[user_id] if now - t < 5]

            if len(self.cooldowns[user_id]) > 5:
                await message.delete()
                strikes = self.add_strike(user_id)
                await self.log_action(guild, f"⚠️ Spam detected from {message.author} — Strike {strikes}")
                return

        # -----------------------------
        # Anti-Link
        # -----------------------------
        if features["anti_link"]:
            if re.search(r"(discord\.gg|http://|https://)", content):
                await message.delete()
                strikes = self.add_strike(user_id)
                await self.log_action(guild, f"🔗 Blocked link from {message.author} — Strike {strikes}")
                return

        # -----------------------------
        # Bad Word Filter
        # -----------------------------
        for word in data["bad_words"]:
            if word in content:
                await message.delete()
                strikes = self.add_strike(user_id)
                await self.log_action(guild, f"🚫 Filtered word from {message.author} — Strike {strikes}")
                return

        # -----------------------------
        # Anti-Mass-Mention
        # -----------------------------
        if features["anti_massmention"]:
            if len(message.mentions) >= limits["massmention"]:
                await message.delete()
                strikes = self.add_strike(user_id)
                await self.log_action(guild, f"📢 Mass mention blocked — {message.author} — Strike {strikes}")
                return

        # -----------------------------
        # Anti-Emoji-Spam
        # -----------------------------
        if features["anti_emojispam"]:
            emoji_count = sum(char in discord.emoji.EMOJI_DATA for char in message.content)
            if emoji_count >= limits["emojis"]:
                await message.delete()
                strikes = self.add_strike(user_id)
                await self.log_action(guild, f"🤣 Emoji spam blocked — {message.author} — Strike {strikes}")
                return

        # -----------------------------
        # Anti-Caps
        # -----------------------------
        if features["anti_caps"]:
            caps = sum(1 for c in message.content if c.isupper())
            if caps >= limits["caps"]:
                await message.delete()
                strikes = self.add_strike(user_id)
                await self.log_action(guild, f"🔠 Caps spam blocked — {message.author} — Strike {strikes}")
                return

        # -----------------------------
        # Anti-Attachment-Spam
        # -----------------------------
        if features["anti_attachmentspam"]:
            if message.attachments:
                now = time.time()
                self.attachment_tracker.setdefault(user_id, []).append(now)
                self.attachment_tracker[user_id] = [
                    t for t in self.attachment_tracker[user_id] if now - t < 10
                ]

                if len(self.attachment_tracker[user_id]) >= limits["attachments"]:
                    await message.delete()
                    strikes = self.add_strike(user_id)
                    await self.log_action(guild, f"📎 Attachment spam — {message.author} — Strike {strikes}")
                    return

        # -----------------------------
        # Anti-Ghost-Ping
        # -----------------------------
        if features["anti_ghostping"]:
            if message.mentions:
                message._automod_mentions = [m.id for m in message.mentions]

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message or not hasattr(message, "_automod_mentions"):
            return

        data = self.load()
        if not data["features"]["anti_ghostping"]:
            return

        if message.author.bot:
            return

        if message.author.guild_permissions.manage_messages:
            return

        if message._automod_mentions:
            strikes = self.add_strike(message.author.id)
            await self.log_action(message.guild, f"👻 Ghost ping detected — {message.author} — Strike {strikes}")

    # -----------------------------
    # Setup
    # -----------------------------
async def setup(bot):
    await bot.add_cog(AutoMod(bot))
