import discord
from discord.ext import commands
import json
import os

TICKET_FILE = "tickets.json"


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists(TICKET_FILE):
            with open(TICKET_FILE, "w") as f:
                json.dump({"ticket_count": 0, "log_channel": None}, f, indent=4)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load(self):
        with open(TICKET_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(TICKET_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Ticket Panel Command
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to open a support ticket.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=TicketPanel(self))

    # -----------------------------
    # Set Log Channel
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def ticketlog(self, ctx, channel: discord.TextChannel):
        data = self.load()
        data["log_channel"] = channel.id
        self.save(data)
        await ctx.send(f"📒 Ticket logs will be sent to {channel.mention}")

    # -----------------------------
    # Create Ticket Channel
    # -----------------------------
    async def create_ticket(self, interaction: discord.Interaction):
        data = self.load()
        data["ticket_count"] += 1
        ticket_number = data["ticket_count"]
        self.save(data)

        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Allow staff roles
        for role in guild.roles:
            if role.permissions.manage_messages:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{ticket_number}",
            overwrites=overwrites,
            reason="New support ticket"
        )

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_number}",
            description="A staff member will be with you shortly.\n\nPress **Close Ticket** when you're done.",
            color=discord.Color.yellow()
        )

        await channel.send(f"{user.mention}", embed=embed, view=CloseTicket(self))

        await interaction.response.send_message(
            f"🎫 Your ticket has been created: {channel.mention}",
            ephemeral=True
        )

    # -----------------------------
    # Close Ticket
    # -----------------------------
    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        data = self.load()
        log_channel_id = data.get("log_channel")
        log_channel = guild.get_channel(log_channel_id) if log_channel_id else None

        # Send transcript/log
        if log_channel:
            messages = await channel.history(limit=200).flatten()
            transcript = "\n".join([f"{m.author}: {m.content}" for m in reversed(messages)])

            if len(transcript) < 1900:
                await log_channel.send(
                    f"📄 **Transcript for {channel.name}:**\n```\n{transcript}\n```"
                )
            else:
                await log_channel.send(
                    f"📄 Transcript for {channel.name} was too long to send."
                )

        await interaction.response.send_message("🗑 Closing ticket...", ephemeral=True)
        await channel.delete(reason="Ticket closed")


# -----------------------------
# Ticket Panel Button
# -----------------------------
class TicketPanel(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.create_ticket(interaction)


# -----------------------------
# Close Ticket Button
# -----------------------------
class CloseTicket(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.close_ticket(interaction)


# -----------------------------
# Setup
# -----------------------------
async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
