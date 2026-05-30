import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📜 All Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )

        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            if not commands_list:
                continue

            cmd_text = ""
            for cmd in commands_list:
                if not cmd.hidden:
                    cmd_text += f"**!{cmd.name}** – {cmd.help or 'No description'}\n"

            if cmd_text:
                embed.add_field(name=f"{cog_name}", value=cmd_text, inline=False)

        # Also include commands not in a cog
        other_cmds = []
        for cmd in self.bot.commands:
            if not cmd.cog_name and not cmd.hidden:
                other_cmds.append(f"**!{cmd.name}** – {cmd.help or 'No description'}")

        if other_cmds:
            embed.add_field(name="Other Commands", value="\n".join(other_cmds), inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
