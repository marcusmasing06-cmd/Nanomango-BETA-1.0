import discord
from discord.ext import commands
import json
import os

LEVELROLES_FILE = "levelroles.json"


class LevelRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create file if missing
        if not os.path.exists(LEVELROLES_FILE):
            with open(LEVELROLES_FILE, "w") as f:
                json.dump({"roles": {}}, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(LEVELROLES_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(LEVELROLES_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Commands
    # -----------------------------
    @commands.group()
    @commands.has_permissions(manage_roles=True)
    async def levelrole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Commands: `add`, `remove`, `list`")

    @levelrole.command()
    async def add(self, ctx, level: int, role: discord.Role):
        data = self.load()
        data["roles"][str(level)] = role.id
        self.save(data)

        await ctx.send(f"✅ Users will now receive **{role.name}** at level **{level}**.")

    @levelrole.command()
    async def remove(self, ctx, level: int):
        data = self.load()

        if str(level) not in data["roles"]:
            return await ctx.send("❌ No role is assigned to that level.")

        del data["roles"][str(level)]
        self.save(data)

        await ctx.send(f"🗑 Removed level role for level **{level}**.")

    @levelrole.command()
    async def list(self, ctx):
        data = self.load()
        roles = data["roles"]

        if not roles:
            return await ctx.send("📭 No level roles set.")

        embed = discord.Embed(
            title="🏅 Level Roles",
            color=discord.Color.gold()
        )

        for level, role_id in roles.items():
            role = ctx.guild.get_role(role_id)
            embed.add_field(
                name=f"Level {level}",
                value=role.name if role else "❌ Role missing",
                inline=False
            )

        await ctx.send(embed=embed)

    # -----------------------------
    # Level-Up Listener
    # -----------------------------
    async def give_level_role(self, member, new_level):
        data = self.load()
        roles = data["roles"]

        if str(new_level) not in roles:
            return

        role_id = roles[str(new_level)]
        role = member.guild.get_role(role_id)

        if not role:
            return

        # Remove older level roles
        for lvl, rid in roles.items():
            if lvl != str(new_level):
                old_role = member.guild.get_role(rid)
                if old_role in member.roles:
                    await member.remove_roles(old_role)

        # Give new role
        await member.add_roles(role)

    # -----------------------------
    # Hook for your leveling system
    # -----------------------------
    @commands.Cog.listener()
    async def on_member_level_up(self, member, new_level):
        await self.give_level_role(member, new_level)


async def setup(bot):
    await bot.add_cog(LevelRoles(bot))
