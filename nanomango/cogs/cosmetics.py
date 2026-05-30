import discord
from discord.ext import commands
import json
import os
import aiofiles
from PIL import Image, ImageDraw

ECON_FILE = "economy.json"
COSMETICS_FILE = "cosmetics.json"
COSMETICS_DIR = "cosmetics"

# -----------------------------
# AUTO-GENERATE COSMETIC IMAGES
# -----------------------------
def ensure_cosmetic_images():
    base = COSMETICS_DIR
    folders = [
        f"{base}/backgrounds",
        f"{base}/frames",
        f"{base}/badges"
    ]

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # -----------------------------
    # Cool Background
    # -----------------------------
    bg1 = f"{base}/backgrounds/cool_background.png"
    if not os.path.exists(bg1):
        img = Image.new("RGBA", (200, 200), (30, 30, 40))
        draw = ImageDraw.Draw(img)
        for x in range(0, 200, 20):
            draw.line((x, 0, x, 200), fill=(50, 50, 70))
        for y in range(0, 200, 20):
            draw.line((0, y, 200, y), fill=(50, 50, 70))
        img.save(bg1)

    # -----------------------------
    # Neon Grid Background
    # -----------------------------
    bg2 = f"{base}/backgrounds/neon_grid.png"
    if not os.path.exists(bg2):
        img = Image.new("RGBA", (200, 200), (10, 10, 20))
        draw = ImageDraw.Draw(img)
        for x in range(0, 200, 25):
            draw.line((x, 0, x, 200), fill=(0, 255, 255))
        for y in range(0, 200, 25):
            draw.line((0, y, 200, y), fill=(0, 255, 255))
        img.save(bg2)

    # -----------------------------
    # Golden Frame
    # -----------------------------
    frame = f"{base}/frames/golden_frame.png"
    if not os.path.exists(frame):
        img = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 179, 179), outline=(255, 215, 0), width=10)
        img.save(frame)

    # -----------------------------
    # Mango Badge
    # -----------------------------
    badge = f"{base}/badges/mango.png"
    if not os.path.exists(badge):
        img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((4, 4, 44, 44), fill=(255, 200, 0))
        draw.ellipse((10, 10, 38, 38), fill=(255, 170, 0))
        img.save(badge)

# Run generator
ensure_cosmetic_images()

# -----------------------------
# DEFAULT ITEMS
# -----------------------------
DEFAULT_ITEMS = {
    "cool_background": {
        "type": "background",
        "price": 250,
        "file": "backgrounds/cool_background.png",
        "description": "A cool grid background."
    },
    "neon_grid": {
        "type": "background",
        "price": 400,
        "file": "backgrounds/neon_grid.png",
        "description": "A glowing neon grid."
    },
    "golden_frame": {
        "type": "frame",
        "price": 500,
        "file": "frames/golden_frame.png",
        "description": "A shiny golden frame."
    },
    "mango_badge": {
        "type": "badge",
        "price": 1000,
        "file": "badges/mango.png",
        "description": "Official Mango badge."
    }
}


class Cosmetics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create cosmetics.json if missing
        if not os.path.exists(COSMETICS_FILE):
            with open(COSMETICS_FILE, "w") as f:
                json.dump({"items": DEFAULT_ITEMS}, f, indent=4)

    # -----------------------------
    # JSON Helpers
    # -----------------------------
    async def load_json(self, path):
        async with aiofiles.open(path, "r") as f:
            content = await f.read() or "{}"
            return json.loads(content)

    async def save_json(self, path, data):
        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(data, indent=4))

    # -----------------------------
    # Ensure user exists
    # -----------------------------
    async def ensure_user(self, user_id):
        data = await self.load_json(ECON_FILE)

        if user_id not in data:
            data[user_id] = {
                "mangos": 0,
                "inventory": [],
                "equipped": {
                    "background": None,
                    "frame": None,
                    "badges": []
                }
            }

        # Ensure new fields exist
        if "inventory" not in data[user_id]:
            data[user_id]["inventory"] = []
        if "equipped" not in data[user_id]:
            data[user_id]["equipped"] = {
                "background": None,
                "frame": None,
                "badges": []
            }

        await self.save_json(ECON_FILE, data)
        return data

    # -----------------------------
    # SHOP
    # -----------------------------
    @commands.command()
    async def shop(self, ctx):
        cos = await self.load_json(COSMETICS_FILE)
        items = cos["items"]

        econ = await self.ensure_user(str(ctx.author.id))
        user = econ[str(ctx.author.id)]

        embed = discord.Embed(
            title="🛒 Mango Cosmetics Shop",
            color=discord.Color.yellow()
        )

        for name, info in items.items():
            owned = name in user["inventory"]
            equipped = (
                user["equipped"].get("background") == name or
                user["equipped"].get("frame") == name or
                name in user["equipped"].get("badges", [])
            )

            status = []
            if owned:
                status.append("Owned")
            if equipped:
                status.append("Equipped")

            status_text = f" ({', '.join(status)})" if status else ""

            embed.add_field(
                name=f"{name}{status_text}",
                value=f"{info['price']} Mangos\n{info['description']}",
                inline=False
            )

        await ctx.send(embed=embed)

    # -----------------------------
    # BUY
    # -----------------------------
    @commands.command()
    async def buy(self, ctx, item_name: str):
        user_id = str(ctx.author.id)
        econ = await self.ensure_user(user_id)
        user = econ[user_id]

        cos = await self.load_json(COSMETICS_FILE)
        items = cos["items"]

        if item_name not in items:
            return await ctx.send("❌ That item doesn't exist.")

        item = items[item_name]

        if user["mangos"] < item["price"]:
            return await ctx.send("❌ Not enough Mangos.")

        if item_name in user["inventory"]:
            return await ctx.send("❌ You already own this item.")

        user["mangos"] -= item["price"]
        user["inventory"].append(item_name)

        await self.save_json(ECON_FILE, econ)
        await ctx.send(f"🛍 You bought **{item_name}**!")

    # -----------------------------
    # INVENTORY
    # -----------------------------
    @commands.command()
    async def inventory(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)

        econ = await self.ensure_user(user_id)
        user = econ[user_id]

        if not user["inventory"]:
            return await ctx.send("🎒 Inventory is empty.")

        embed = discord.Embed(
            title=f"{member.name}'s Inventory",
            color=discord.Color.yellow()
        )

        for item in user["inventory"]:
            embed.add_field(name=item, value="Owned", inline=False)

        await ctx.send(embed=embed)

    # -----------------------------
    # EQUIP BACKGROUND
    # -----------------------------
    @commands.command()
    async def equipbackground(self, ctx, item_name: str):
        user_id = str(ctx.author.id)
        econ = await self.ensure_user(user_id)
        user = econ[user_id]

        if item_name not in user["inventory"]:
            return await ctx.send("❌ You don't own that background.")

        cos = await self.load_json(COSMETICS_FILE)
        if item_name not in cos["items"] or cos["items"][item_name]["type"] != "background":
            return await ctx.send("❌ That is not a background.")

        user["equipped"]["background"] = item_name
        await self.save_json(ECON_FILE, econ)

        await ctx.send(f"🖼 Equipped background **{item_name}**.")

    # -----------------------------
    # EQUIP FRAME
    # -----------------------------
    @commands.command()
    async def equipframe(self, ctx, item_name: str):
        user_id = str(ctx.author.id)
        econ = await self.ensure_user(user_id)
        user = econ[user_id]

        if item_name not in user["inventory"]:
            return await ctx.send("❌ You don't own that frame.")

        cos = await self.load_json(COSMETICS_FILE)
        if item_name not in cos["items"] or cos["items"][item_name]["type"] != "frame":
            return await ctx.send("❌ That is not a frame.")

        user["equipped"]["frame"] = item_name
        await self.save_json(ECON_FILE, econ)

        await ctx.send(f"🎨 Equipped frame **{item_name}**.")

    # -----------------------------
    # EQUIP BADGE
    # -----------------------------
    @commands.command()
    async def equipbadge(self, ctx, item_name: str):
        user_id = str(ctx.author.id)
        econ = await self.ensure_user(user_id)
        user = econ[user_id]

        if item_name not in user["inventory"]:
            return await ctx.send("❌ You don't own that badge.")

        cos = await self.load_json(COSMETICS_FILE)
        if item_name not in cos["items"] or cos["items"][item_name]["type"] != "badge":
            return await ctx.send("❌ That is not a badge.")

        if len(user["equipped"]["badges"]) >= 3:
            return await ctx.send("❌ You can only equip 3 badges.")

        if item_name in user["equipped"]["badges"]:
            return await ctx.send("❌ Badge already equipped.")

        user["equipped"]["badges"].append(item_name)
        await self.save_json(ECON_FILE, econ)

        await ctx.send(f"🏅 Equipped badge **{item_name}**.")

    # -----------------------------
    # UNEQUIP BADGE
    # -----------------------------
    @commands.command()
    async def unequipbadge(self, ctx, item_name: str):
        user_id = str(ctx.author.id)
        econ = await self.ensure_user(user_id)
        user = econ[user_id]

        if item_name not in user["equipped"]["badges"]:
            return await ctx.send("❌ That badge is not equipped.")

        user["equipped"]["badges"].remove(item_name)
        await self.save_json(ECON_FILE, econ)

        await ctx.send(f"🏅 Unequipped badge **{item_name}**.")


async def setup(bot):
    await bot.add_cog(Cosmetics(bot))
