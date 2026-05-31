import discord
from discord.ext import commands
import json
import os
from PIL import Image, ImageDraw, ImageFont
import aiofiles
import io

# -----------------------------
# Path setup (works on Railway)
# -----------------------------
# This file is: nanomango/cogs/leveling.py
# BASE_DIR = nanomango/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)  # repo root

LEVEL_FILE = os.path.join(BASE_DIR, "levels.json")
ECON_FILE = os.path.join(BASE_DIR, "economy.json")
COSMETICS_FILE = os.path.join(BASE_DIR, "cosmetics.json")
COSMETICS_FOLDER = os.path.join(BASE_DIR, "cosmetics")
FONT_PATH = os.path.join(ROOT_DIR, "arial.ttf")  # arial.ttf in repo root


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Ensure levels.json exists
        if not os.path.exists(LEVEL_FILE):
            with open(LEVEL_FILE, "w") as f:
                json.dump({}, f)

        # Ensure economy.json exists (so rank doesn't crash)
        if not os.path.exists(ECON_FILE):
            with open(ECON_FILE, "w") as f:
                json.dump({}, f)

        # Ensure cosmetics.json exists (basic structure)
        if not os.path.exists(COSMETICS_FILE):
            with open(COSMETICS_FILE, "w") as f:
                json.dump({"items": {}}, f)

    # -----------------------------
    # Load & Save
    # -----------------------------
    async def load_data(self):
        async with aiofiles.open(LEVEL_FILE, "r") as f:
            content = await f.read() or "{}"
            return json.loads(content)

    async def save_data(self, data):
        async with aiofiles.open(LEVEL_FILE, "w") as f:
            await f.write(json.dumps(data, indent=4))

    # -----------------------------
    # XP on message
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = await self.load_data()
        user_id = str(message.author.id)

        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 1}

        # XP gain
        data[user_id]["xp"] += 5

        # Level-up check (1000 XP per level)
        xp = data[user_id]["xp"]
        level = data[user_id]["level"]
        needed = level * 1000

        if xp >= needed:
            data[user_id]["level"] += 1
            await message.channel.send(
                f"🎉 **{message.author.name}** leveled up to **Level {data[user_id]['level']}**!"
            )

        await self.save_data(data)

    # -----------------------------
    # Fetch avatar
    # -----------------------------
    async def fetch_pfp(self, member):
        avatar = member.display_avatar.replace(size=256)
        data = await avatar.read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        img = img.resize((150, 150))
        return img

    # -----------------------------
    # Rank Card Generator
    # -----------------------------
    def generate_rank_card(self, member, level, xp, pfp_img, rank_position):
        width, height = 900, 300
        img = Image.new("RGBA", (width, height), (18, 18, 18, 255))
        draw = ImageDraw.Draw(img)

        # Load economy + cosmetics safely
        try:
            with open(ECON_FILE, "r") as f:
                econ = json.load(f)
        except:
            econ = {}

        try:
            with open(COSMETICS_FILE, "r") as f:
                cos_root = json.load(f)
                cos = cos_root.get("items", {})
        except:
            cos = {}

        user_id = str(member.id)
        equipped = econ.get(user_id, {}).get("equipped", {
            "background": None,
            "frame": None,
            "badges": []
        })

        # -----------------------------
        # Background (tiled)
        # -----------------------------
        bg_name = equipped.get("background")
        if bg_name and bg_name in cos:
            bg_path = os.path.join(COSMETICS_FOLDER, cos[bg_name]["file"])
            if os.path.exists(bg_path):
                bg_img = Image.open(bg_path).convert("RGBA")
                bw, bh = bg_img.size
                for x in range(0, width, bw):
                    for y in range(0, height, bh):
                        img.alpha_composite(bg_img, (x, y))

        # Dark overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 90))
        img.alpha_composite(overlay)

        # Colors
        mango_yellow = (255, 210, 70)
        text_white = (255, 255, 255)
        text_gray = (180, 180, 180)

        # Fonts (fallback if font missing)
        try:
            font_big = ImageFont.truetype(FONT_PATH, 42)
            font_small = ImageFont.truetype(FONT_PATH, 28)
            font_tiny = ImageFont.truetype(FONT_PATH, 22)
            wm_font = ImageFont.truetype(FONT_PATH, 26)
        except:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_tiny = ImageFont.load_default()
            wm_font = ImageFont.load_default()

        # Left stripe
        draw.rectangle([(0, 0), (25, height)], fill=mango_yellow)

        # Username
        draw.text((200, 40), member.name, font=font_big, fill=text_white)

        # Rank
        draw.text((200, 95), f"Rank #{rank_position}", font=font_small, fill=mango_yellow)

        # Level
        draw.text((200, 135), f"Level {level}", font=font_small, fill=text_white)

        # XP
        xp_needed = level * 1000
        progress = xp / xp_needed if xp_needed > 0 else 0

        draw.text((200, 170), f"Total XP: {xp}", font=font_tiny, fill=text_gray)
        draw.text((200, 205), f"{xp} / {xp_needed} XP", font=font_tiny, fill=text_gray)

        # XP bar
        bar_x = 200
        bar_y = 240
        bar_width = 600
        bar_height = 28

        draw.rounded_rectangle(
            [(bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height)],
            radius=12,
            fill=(40, 40, 40)
        )

        draw.rounded_rectangle(
            [(bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height)],
            radius=12,
            fill=mango_yellow
        )

        # Avatar (rounded)
        mask = Image.new("L", pfp_img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, pfp_img.size[0], pfp_img.size[1]), fill=255)
        pfp_img.putalpha(mask)

        img.paste(pfp_img, (25, 75), pfp_img)

        # Frame
        frame_name = equipped.get("frame")
        if frame_name and frame_name in cos:
            frame_path = os.path.join(COSMETICS_FOLDER, cos[frame_name]["file"])
            if os.path.exists(frame_path):
                frame_img = Image.open(frame_path).convert("RGBA")
                frame_img = frame_img.resize(pfp_img.size)
                img.alpha_composite(frame_img, (25, 75))

        # Badges
        badges = equipped.get("badges", [])[:3]
        badge_size = 48
        padding = 10
        x = width - padding - badge_size
        y = padding

        for badge_name in badges:
            if badge_name not in cos:
                continue
            badge_path = os.path.join(COSMETICS_FOLDER, cos[badge_name]["file"])
            if not os.path.exists(badge_path):
                continue

            badge_img = Image.open(badge_path).convert("RGBA")
            badge_img = badge_img.resize((badge_size, badge_size))
            img.alpha_composite(badge_img, (x, y))
            x -= badge_size + 8

        # Watermark
        draw.text(
            (width - 180, height - 40),
            "NanoMango",
            font=wm_font,
            fill=(255, 255, 255, 60)
        )

        return img

    # -----------------------------
    # Rank Command
    # -----------------------------
    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        data = await self.load_data()
        user_id = str(member.id)

        if user_id not in data:
            return await ctx.send("This user has no XP yet.")

        # Rank position
        sorted_users = sorted(
            data.items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )

        rank_position = next(
            (i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id),
            None
        )

        level = data[user_id]["level"]
        xp = data[user_id]["xp"]

        # Fetch avatar using helper
        pfp = await self.fetch_pfp(member)

        img = self.generate_rank_card(member, level, xp, pfp, rank_position)

        # Save to bytes instead of disk (safer on Railway)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        file = discord.File(buf, filename="rank.png")
        await ctx.send(file=file)

    # -----------------------------
    # Leaderboard Command
    # -----------------------------
    @commands.command()
    async def leaderboard(self, ctx):
        data = await self.load_data()

        sorted_users = sorted(
            data.items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )

        embed = discord.Embed(
            title="🏆 NanoMango Leaderboard",
            color=discord.Color.yellow()
        )

        for i, (user_id, stats) in enumerate(sorted_users[:10], start=1):
            user = self.bot.get_user(int(user_id))
            embed.add_field(
                name=f"{i}. {user.name if user else 'Unknown'}",
                value=f"Level {stats['level']} — {stats['xp']} XP",
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
