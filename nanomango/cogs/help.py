import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📜 All Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )

        # Command descriptions dictionary
        descriptions = {
            "warn": "Issue a warning to a user and log it.",
            "warns": "View all warnings a user has received.",
            "clearwarns": "Remove all warnings from a user.",

            "rank": "Show your rank card with XP and level.",
            "leaderboard": "Display the top users by XP.",

            "kick": "Remove a user from the server.",
            "ban": "Ban a user from the server.",
            "unban": "Unban a previously banned user.",
            "clear": "Delete a number of messages in a channel.",
            "mute": "Prevent a user from speaking in the server.",
            "unmute": "Restore a muted user’s ability to speak.",

            "help": "Show all available commands and categories.",

            "ticketpanel": "Create the ticket panel with buttons.",
            "ticketlog": "Set the channel where ticket logs are sent.",

            "autorole": "Configure automatic role assignment for new members.",

            "setwelcome": "Set the welcome channel.",
            "welcomemsg": "Set the welcome message template.",
            "welcomestatus": "Enable or disable the welcome system.",

            "levelrole": "Assign roles that unlock at specific levels.",

            "addresponse": "Add an automatic response trigger.",
            "delresponse": "Delete an automatic response trigger.",
            "responses": "List all auto-response triggers.",

            "setstats": "Create the server statistics channels.",
            "statsreset": "Reset and recreate the stat channels.",
            "statsstatus": "Enable or disable the stats system.",

            "rrpanel": "Create the reaction-role control panel.",
            "reactionrole": "Add or remove a reaction-role entry.",

            "antiraid": "Configure anti-raid protection settings.",

            "afk": "Set yourself as AFK with an optional message.",

            "setlog": "Set the logging channel.",
            "logstatus": "Enable or disable the logging system.",

            "reload": "Reload a bot extension.",
            "load": "Load a bot extension.",
            "unload": "Unload a bot extension.",
            "shutdown": "Shut down the bot safely.",
            "restart": "Restart the bot.",

            "meme": "Send a random meme.",
            "cat": "Send a random cat picture.",
            "dog": "Send a random dog picture.",
            "avatar": "Show a user’s avatar.",
            "say": "Make the bot repeat your message.",
            "_8ball": "Ask the magic 8-ball a question.",
            "joke": "Send a random joke.",
            "fact": "Send a random fun fact.",
            "reverse": "Reverse the given text.",
            "rate": "Rate something from 1 to 10.",
            "ship": "Ship two users together.",
            "gif": "Search for a GIF.",
            "quote": "Send a random inspirational quote.",
            "topic": "Generate a random conversation topic.",
            "roast": "Roast a user with a random insult.",
            "compliment": "Compliment a user with something nice.",

            "shop": "View all available cosmetic items.",
            "buy": "Purchase a cosmetic item.",
            "inventory": "View your owned cosmetics.",
            "equipbackground": "Equip a background for your rank card.",
            "equipframe": "Equip a frame for your rank card.",
            "equipbadge": "Equip a badge.",
            "unequipbadge": "Unequip a badge.",

            "balance": "Check your current coin balance.",
            "daily": "Claim your daily reward.",
            "weekly": "Claim your weekly reward.",
            "work": "Earn coins by working.",
            "pay": "Send coins to another user.",
            "mangos": "View your mango currency balance.",

            "ping": "Check the bot’s latency.",
            "uptime": "Show how long the bot has been online.",
            "userinfo": "Display information about a user.",
            "serverinfo": "Display information about the server.",
            "invite": "Get the bot’s invite link.",
            "poll": "Create a reaction-based poll.",
            "remind": "Set a reminder.",

            "automod": "Configure automatic moderation settings.",

            "setsuggest": "Set the suggestion channel.",
            "suggest": "Submit a suggestion.",
            "suggestinfo": "View information about the suggestion system.",

            "starboard": "Configure the starboard system."
        }

        for cog_name, cog in self.bot.cogs.items():

            # Skip help cog
            if cog_name.lower() == "helpcommand":
                continue

            # Skip giveaways if it exists
            if cog_name.lower() == "giveaways":
                continue

            commands_list = cog.get_commands()
            if not commands_list:
                continue

            cmd_text = ""
            for cmd in commands_list:
                if cmd.hidden:
                    continue

                desc = descriptions.get(cmd.name, "No description.")
                cmd_text += f"**!{cmd.name}** — {desc}\n"

            if cmd_text:
                embed.add_field(name=f"{cog_name}", value=cmd_text, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
