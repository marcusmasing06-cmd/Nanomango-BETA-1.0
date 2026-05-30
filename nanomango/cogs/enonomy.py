import discord
from discord.ext import commands
import json
import os
import aiofiles
import asyncio

ECON_FILE = "economy.json"

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(ECON_FILE):
            with open(ECON_FILE, "w") as f:
                json.dump({}, f)

    # -----------------------------
    # Load & Save
    # -----------------------------
    async def load(self, file):
        async with aiofiles.open(file, "r") as f:
            content = await f.read() or "{}"
            return json.loads(content)

    async def save(self, file, data):
        async with aiofiles.open(file, "w") as f:
            await f.write(json.dumps(data, indent=4))

    # -----------------------------
    # Ensure user exists
    # -----------------------------
    async def ensure_user(self, user_id):
        data = await self.load(ECON_FILE)
        if user_id not in data:
            data[user_id] = {
                "mangos": 0,
                "inventory": [],   # still used by cosmetics
                "equipped": {      # cosmetics system uses this
                    "background": None,
                    "frame": None,
                    "badges": []
                }
            }
            await self.save(ECON_FILE, data)
        return data

    # -----------------------------
    # Balance
    # -----------------------------
    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data = await self.ensure_user(str(member.id))
        bal = data[str(member.id)]["mangos"]
        await ctx.send(f"💰 **{member.name}** has **{bal} Mangos**")

    # -----------------------------
    # Daily
    # -----------------------------
    @commands.command()
    async def daily(self, ctx):
        user = str(ctx.author.id)
        data = await self.ensure_user(user)

        now = asyncio.get_event_loop().time()
        if "daily_cd" in data[user] and now - data[user]["daily_cd"] < 86400:
            return await ctx.send("⏳ You already claimed your daily Mangos.")

        data[user]["daily_cd"] = now
        data[user]["mangos"] += 150
        await self.save(ECON_FILE, data)

        await ctx.send("🌅 You claimed **150 Mangos**!")

    # -----------------------------
    # Weekly
    # -----------------------------
    @commands.command()
    async def weekly(self, ctx):
        user = str(ctx.author.id)
        data = await self.ensure_user(user)

        now = asyncio.get_event_loop().time()
        if "weekly_cd" in data[user] and now - data[user]["weekly_cd"] < 604800:
            return await ctx.send("⏳ You already claimed your weekly Mangos.")

        data[user]["weekly_cd"] = now
        data[user]["mangos"] += 500
        await self.save(ECON_FILE, data)

        await ctx.send("📅 You claimed **500 Mangos**!")

    # -----------------------------
    # Work
    # -----------------------------
    @commands.command()
    async def work(self, ctx):
        user = str(ctx.author.id)
        data = await self.ensure_user(user)

        now = asyncio.get_event_loop().time()
        if "work_cd" in data[user] and now - data[user]["work_cd"] < 3600:
            return await ctx.send("⏳ You can work again in 1 hour.")

        import random
        earned = random.randint(50, 120)

        data[user]["work_cd"] = now
        data[user]["mangos"] += earned
        await self.save(ECON_FILE, data)

        await ctx.send(f"🛠 You worked and earned **{earned} Mangos**!")

    # -----------------------------
    # Pay
    # -----------------------------
    @commands.command()
    async def pay(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Invalid amount.")

        sender = str(ctx.author.id)
        receiver = str(member.id)

        data = await self.ensure_user(sender)
        await self.ensure_user(receiver)

        if data[sender]["mangos"] < amount:
            return await ctx.send("❌ You don't have enough Mangos.")

        data[sender]["mangos"] -= amount
        data[receiver]["mangos"] += amount

        await self.save(ECON_FILE, data)
        await ctx.send(f"💸 Sent **{amount} Mangos** to **{member.name}**")

    # -----------------------------
    # Mango Leaderboard
    # -----------------------------
    @commands.command()
    async def mangos(self, ctx):
        data = await self.load(ECON_FILE)

        sorted_users = sorted(data.items(), key=lambda x: x[1]["mangos"], reverse=True)

        embed = discord.Embed(title="🏆 Mango Leaderboard", color=discord.Color.yellow())

        for i, (uid, stats) in enumerate(sorted_users[:10], start=1):
            user = self.bot.get_user(int(uid))
            embed.add_field(
                name=f"{i}. {user.name if user else 'Unknown'}",
                value=f"{stats['mangos']} Mangos",
                inline=False
            )

        await ctx.send(embed=embed)

# -----------------------------
# Setup
# -----------------------------
async def setup(bot):
    await bot.add_cog(Economy(bot))
