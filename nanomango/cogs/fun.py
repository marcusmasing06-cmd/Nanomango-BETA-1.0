import discord
from discord.ext import commands
import random
import aiohttp


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------
    # Basic Fun Commands
    # -----------------------------
    @commands.command()
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as r:
                data = await r.json()

        embed = discord.Embed(title=data["title"], color=discord.Color.yellow())
        embed.set_image(url=data["url"])
        await ctx.send(embed=embed)

    @commands.command()
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as r:
                data = await r.json()

        await ctx.send(data[0]["url"])

    @commands.command()
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                data = await r.json()

        await ctx.send(data["message"])

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(member.display_avatar.url)

    @commands.command()
    async def say(self, ctx, *, message):
        await ctx.send(message)

    @commands.command()
    async def _8ball(self, ctx, *, question):
        responses = [
            "Yes", "No", "Definitely", "Absolutely not", "Ask again later",
            "Probably", "Unlikely", "100% yes", "100% no"
        ]
        await ctx.send(f"🎱 {random.choice(responses)}")

    # -----------------------------
    # Fun Expansion Pack
    # -----------------------------
    @commands.command()
    async def joke(self, ctx):
        jokes = [
            "Why don’t skeletons fight each other? They don’t have the guts.",
            "I told my computer I needed a break… it said 'No problem, I’ll go to sleep.'",
            "Why did the scarecrow win an award? He was outstanding in his field."
        ]
        await ctx.send(random.choice(jokes))

    @commands.command()
    async def fact(self, ctx):
        facts = [
            "Honey never spoils.",
            "Bananas are berries, but strawberries aren’t.",
            "Octopuses have three hearts.",
            "A day on Venus is longer than a year on Venus."
        ]
        await ctx.send(random.choice(facts))

    @commands.command()
    async def reverse(self, ctx, *, text):
        await ctx.send(text[::-1])

    @commands.command()
    async def rate(self, ctx, *, thing):
        score = random.randint(1, 100)
        await ctx.send(f"I rate **{thing}** a **{score}/100**")

    @commands.command()
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member):
        score = random.randint(1, 100)
        await ctx.send(f"💞 **{user1.name}** × **{user2.name}** = **{score}%** compatibility")

    @commands.command()
    async def gif(self, ctx, *, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.giphy.com/v1/gifs/search?api_key=dc6zaTOxFJmz&q={query}&limit=1"
            ) as r:
                data = await r.json()

        if data["data"]:
            await ctx.send(data["data"][0]["images"]["original"]["url"])
        else:
            await ctx.send("No GIFs found.")

    @commands.command()
    async def quote(self, ctx):
        quotes = [
            "Believe you can and you're halfway there.",
            "Dream big and dare to fail.",
            "The best time to plant a tree was 20 years ago. The second best time is now."
        ]
        await ctx.send(random.choice(quotes))

    @commands.command()
    async def topic(self, ctx):
        topics = [
            "What’s the best game you’ve ever played?",
            "If you could live anywhere, where would it be?",
            "What’s a hobby you want to learn?",
            "What’s your favorite childhood memory?"
        ]
        await ctx.send(random.choice(topics))

    @commands.command()
    async def roast(self, ctx, member: discord.Member):
        roasts = [
            "You're not stupid — you just have bad luck thinking.",
            "If I wanted to kill myself, I’d climb your ego and jump to your IQ.",
            "You have the personality of wet cardboard."
        ]
        await ctx.send(f"{member.mention} {random.choice(roasts)}")

    @commands.command()
    async def compliment(self, ctx, member: discord.Member):
        compliments = [
            "You're awesome.",
            "You make people smile.",
            "You're smarter than you think.",
            "You're genuinely a good person."
        ]
        await ctx.send(f"{member.mention} {random.choice(compliments)}")


async def setup(bot):
    await bot.add_cog(Fun(bot))
