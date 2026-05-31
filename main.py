import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

async def load_cogs():
    for filename in os.listdir("./nanomango/cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"nanomango.cogs.{filename[:-3]}")
            print(f"Loaded {filename}")

@bot.event
async def on_ready():
    print(f"NanoMango is online as {bot.user}")

    # Set presence: Watching ⚙️ Running NanoMango
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="⚙️ Running NanoMango"
        )
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
