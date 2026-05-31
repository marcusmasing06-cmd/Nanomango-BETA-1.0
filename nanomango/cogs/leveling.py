import discord
from discord.ext import commands
import json
import os
from PIL import Image, ImageDraw, ImageFont
import aiofiles
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

LEVEL_FILE = os.path.join(BASE_DIR, "levels.json")
ECON_FILE = os.path.join(BASE_DIR, "economy.json")
COSMETICS_FILE = os.path.join(BASE_DIR, "cosmetics.json")
COSMETICS_FOLDER = os.path.join(BASE_DIR, "cosmetics")
FONT_PATH = os.path.join(ROOT_DIR, "arial.ttf")


class Leveling(commands.Cog):
    """XP, leveling, rank cards, and leaderboard."""

    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(LEVEL_FILE):
            with open(LEVEL_FILE, "w") as f:
                json.dump({}, f)

        if not os.path.exists(ECON_FILE):
            with open(ECON_FILE, "w") as f:
                json.dump({}, f)

        if not os.path.exists(COSMETICS_FILE):
            with open(COSMETICS_FILE, "w") as f:
                json.dump({"items": {}}, f)

    async def load_data(self):
        async with aiofiles.open(LEVEL_FILE, "r") as f:
            content = await f.read() or "{}"
            return json.loads(content)

    async def save_data(self, data):
        async with aiofiles.open(LEVEL_FILE, "w") as f:
            await f.write(json.dumps(data, indent=4))

    @commands.Cog.listener()
    async def on_message(self, message):
        """Gives XP when users talk."""
        if message.author.bot:
            return

        data = await self.load_data()
        uid = str(message.author.id)

        if uid not in data:
            data[uid] = {"xp": 0, "level": 1}

        data[uid]["xp"] += 5

        xp = data[uid]["xp"]
        level = data[uid]["level"]
        needed = level * 1000

        if xp >= needed:
            data[uid]["level"] += 1
            await message.channel.send(
                f"🎉 **{message.author.name}** leveled up to **Level {data[uid]['level']}**!"
            )

        await self.save_data(data)

    async def fetch_pfp(self, member):
        avatar = member.display_avatar.replace(size=256)
        data = await avatar.read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        return img.resize((150, 150))

    def generate_rank_card(self, member, level, xp, pfp, rank_position):
        width, height = 900, 300
        img = Image.new("RGBA", (width, height), (18, 18, 18, 255))
        draw = ImageDraw.Draw(img)

        try:
            with open(ECON_FILE, "r") as f:
                econ = json.load(f)
        except:
            econ = {}

        try:
            with open(COSMETICS_FILE, "r") as f:
                cos = json.load(f).get("items", {})
        except:
            cos = {}

        uid = str(member.id)
        equipped = econ.get(uid, {}).get("equipped", {
            "background": None,
            "frame": None,
            "badges": []
        })

        # Background
        bg_name = equipped.get("background")
        if bg_name and bg_name in cos:
            bg_path = os.path.join(COSMETICS_FOLDER, cos[bg_name]["file"])
            if os.path.exists(bg_path):
                bg_img = Image.open(bg_path).convert("RGBA")
                bw, bh = bg_img.size
                for x in range(0, width, bw):
                    for y in range(0, height, bh):
                        img.alpha_composite(bg_img, (x, y))

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 90))
        img.alpha_composite(overlay)

        mango = (255, 210, 70)
        white = (255, 255, 255)
        gray = (180, 180, 180)

        try:
            font_big = ImageFont.truetype(FONT_PATH, 42)
            font_small = ImageFont.truetype(FONT_PATH, 28)
            font_tiny = ImageFont.truetype(FONT_PATH, 22)
            wm_font = ImageFont.truetype(FONT_PATH, 26)
        except:
            font_big = font_small = font_tiny = wm_font = ImageFont.load_default()

        draw.rectangle([(0, 0), (25, height)], fill=mango)

        draw.text((200, 40), member.name, font=font_big, fill=white)
        draw.text((200, 95), f"Rank #{rank_position}", font=font_small, fill=mango)
        draw.text((200, 135), f"Level {level}", font=font_small, fill=white)

        needed = level * 1000
        progress = xp / needed if needed > 0 else 0

        draw.text((200, 170), f"Total XP: {xp}", font=font_tiny, fill=gray)
        draw.text((200, 205), f"{xp} / {needed} XP", font=font_tiny, fill=gray)

        bar_x, bar_y = 200, 240
        bar_w, bar_h = 600, 28

        draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)],
                               radius=12, fill=(40, 40, 40))
        draw.rounded_rectangle([(bar_x, bar_y), (bar_x + int(bar_w * progress), bar_y + bar_h)],
                               radius=12, fill=mango)

        mask = Image.new("L", pfp.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, pfp.size[0], pfp.size[1]), fill=255)
        pfp.putalpha(mask)
        img.paste(pfp, (25, 75), pfp)

        draw.text((width - 180, height - 40), "NanoMango", font=wm_font, fill=(255, 255, 255, 60))

        return img

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Show your rank card."""
        member = member or ctx.author

        data = await self.load_data()
        uid = str(member.id)

        if uid not in data:
            return await ctx.send("This user has no XP yet.")

        sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)
        rank_position = next((i + 1 for i, (u, _) in enumerate(sorted_users) if u == uid), None)

        level = data[uid]["level"]
        xp = data[uid]["xp"]

        pfp = await self.fetch_pfp(member)
        img = self.generate_rank_card(member, level, xp, pfp, rank_position)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        await ctx.send(file=discord.File(buf, filename="rank.png"))

    @commands.command()
    async def leaderboard(self, ctx):
        """Show the top XP users."""
        data = await self.load_data()

        sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)

        embed = discord.Embed(title="🏆 NanoMango Leaderboard", color=discord.Color.yellow())

        for i, (uid, stats) in enumerate(sorted_users[:10], start=1):
            user = self.bot.get_user(int(uid))
            embed.add_field(
                name=f"{i}. {user.name if user else 'Unknown'}",
                value=f"Level {stats['level']} — {stats['xp']} XP",
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
