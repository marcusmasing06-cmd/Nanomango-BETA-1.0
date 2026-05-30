import discord
from discord.ext import commands
import platform
import time
import datetime

start_time = time.time()  # Track uptime


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------------
    # Ping Command
    # -----------------------------
    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! `{latency}ms`")

    # -----------------------------
    # Uptime Command
    # -----------------------------
    @commands.command()
    async def uptime(self, ctx):
        now = time.time()
        diff = int(now - start_time)

        days = diff // 86400
        hours = (diff % 86400) // 3600
        minutes = (diff % 3600) // 60
        seconds = diff % 60

        await ctx.send(
            f"⏱ **Uptime:** {days}d {hours}h {minutes}m {seconds}s"
        )

    # -----------------------------
    # User Info
    # -----------------------------
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        embed = discord.Embed(
            title=f"👤 User Info — {member.name}",
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)

        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)

        await ctx.send(embed=embed)

    # -----------------------------
    # Server Info
    # -----------------------------
    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild

        embed = discord.Embed(
            title=f"🏰 Server Info — {guild.name}",
            color=discord.Color.yellow()
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)

        await ctx.send(embed=embed)

    # -----------------------------
    # Invite Command
    # -----------------------------
    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(
            title="🔗 Invite NanoMango",
            description="[Click here to invite the bot](https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands)",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # -----------------------------
    # Poll Command
    # -----------------------------
    @commands.command()
    async def poll(self, ctx, *, question=None):
        if question is None:
            return await ctx.send("❌ Usage: `!poll <question>`")

        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Poll by {ctx.author}")

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    # -----------------------------
    # Reminder Command
    # -----------------------------
    @commands.command()
    async def remind(self, ctx, time_amount=None, *, reminder=None):
        if time_amount is None or reminder is None:
            return await ctx.send("❌ Usage: `!remind <time> <message>`\nExample: `!remind 10m take a break`")

        # Parse time
        unit = time_amount[-1]
        try:
            value = int(time_amount[:-1])
        except:
            return await ctx.send("❌ Invalid time format. Use `10s`, `5m`, `2h`, etc.")

        seconds = 0
        if unit == "s":
            seconds = value
        elif unit == "m":
            seconds = value * 60
        elif unit == "h":
            seconds = value * 3600
        else:
            return await ctx.send("❌ Invalid time unit. Use `s`, `m`, or `h`.")

        await ctx.send(f"⏰ I’ll remind you in **{time_amount}**.")

        await discord.utils.sleep_until(datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))

        await ctx.send(f"🔔 **Reminder:** {ctx.author.mention} — {reminder}")


async def setup(bot):
    await bot.add_cog(Utility(bot))
