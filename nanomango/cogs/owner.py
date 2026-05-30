import discord
from discord.ext import commands
import os
import sys

class OwnerTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------
    # Check if user is bot owner
    # -----------------------------
    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    # -----------------------------
    # Reload a cog
    # -----------------------------
    @commands.command()
    async def reload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"🔄 Reloaded **{cog}**")
        except Exception as e:
            await ctx.send(f"❌ Error: `{e}`")

    # -----------------------------
    # Load a cog
    # -----------------------------
    @commands.command()
    async def load(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"📥 Loaded **{cog}**")
        except Exception as e:
            await ctx.send(f"❌ Error: `{e}`")

    # -----------------------------
    # Unload a cog
    # -----------------------------
    @commands.command()
    async def unload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"📤 Unloaded **{cog}**")
        except Exception as e:
            await ctx.send(f"❌ Error: `{e}`")

    # -----------------------------
    # Shutdown bot
    # -----------------------------
    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("🛑 Shutting down...")
        await self.bot.close()

    # -----------------------------
    # Restart bot (soft)
    # -----------------------------
    @commands.command()
    async def restart(self, ctx):
        await ctx.send("🔁 Restarting bot...")
        os.execv(sys.executable, ["python"] + sys.argv)


async def setup(bot):
    await bot.add_cog(OwnerTools(bot))
