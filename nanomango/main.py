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
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded {filename}")

@bot.event
async def on_ready():
    print(f"NanoMango is online as {bot.user}")

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


