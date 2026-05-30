import discord
from discord.ext import commands
import json
import os

REACTION_FILE = "reactionroles.json"


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create file if missing
        if not os.path.exists(REACTION_FILE):
            with open(REACTION_FILE, "w") as f:
                json.dump({}, f)

    # -----------------------------
    # Load & Save
    # -----------------------------
    def load_data(self):
        with open(REACTION_FILE, "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open(REACTION_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------------
    # Reaction Role Panel Command
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rrpanel(self, ctx):
        embed = discord.Embed(
            title="🎛 Reaction Role Control Panel",
            description="Use the buttons below to manage reaction roles.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=RRPanel(self))

    # -----------------------------
    # Create Reaction Role (manual)
    # -----------------------------
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def reactionrole(self, ctx, action=None):
        if action is None:
            return await ctx.send("Usage:\n`!reactionrole create`\n`!reactionrole delete`")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # CREATE
        if action.lower() == "create":
            await ctx.send("Send the **message ID** you want to attach reaction roles to.")
            msg_id_msg = await self.bot.wait_for("message", check=check)
            msg_id = int(msg_id_msg.content)

            try:
                target_msg = await ctx.channel.fetch_message(msg_id)
            except:
                return await ctx.send("❌ Invalid message ID.")

            await ctx.send("Now send the **emoji** you want to use.")
            emoji_msg = await self.bot.wait_for("message", check=check)
            emoji = emoji_msg.content

            await ctx.send("Now mention the **role** to give when reacting.")
            role_msg = await self.bot.wait_for("message", check=check)
            role = role_msg.role_mentions[0] if role_msg.role_mentions else None

            if role is None:
                return await ctx.send("❌ You must mention a role.")

            try:
                await target_msg.add_reaction(emoji)
            except:
                return await ctx.send("❌ I cannot react with that emoji.")

            data = self.load_data()
            if str(msg_id) not in data:
                data[str(msg_id)] = {}
            data[str(msg_id)][emoji] = role.id
            self.save_data(data)

            await ctx.send(f"✅ Reaction role added!\nEmoji: {emoji}\nRole: {role.name}")

        # DELETE
        elif action.lower() == "delete":
            await ctx.send("Send the **message ID** to remove reaction roles from.")
            msg_id_msg = await self.bot.wait_for("message", check=check)
            msg_id = msg_id_msg.content

            data = self.load_data()

            if msg_id not in data:
                return await ctx.send("❌ No reaction roles found for that message.")

            del data[msg_id]
            self.save_data(data)

            await ctx.send("🗑 Reaction roles removed for that message.")

    # -----------------------------
    # Add Role on Reaction
    # -----------------------------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member is None or payload.member.bot:
            return

        data = self.load_data()
        msg_id = str(payload.message_id)

        if msg_id not in data:
            return

        emoji = str(payload.emoji)
        if emoji not in data[msg_id]:
            return

        guild = self.bot.get_guild(payload.guild_id)
        role_id = data[msg_id][emoji]
        role = guild.get_role(role_id)

        if role:
            await payload.member.add_roles(role)

    # -----------------------------
    # Remove Role on Reaction Remove
    # -----------------------------
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member is None or member.bot:
            return

        data = self.load_data()
        msg_id = str(payload.message_id)

        if msg_id not in data:
            return

        emoji = str(payload.emoji)
        if emoji not in data[msg_id]:
            return

        role_id = data[msg_id][emoji]
        role = guild.get_role(role_id)

        if role:
            await member.remove_roles(role)


# -----------------------------
# Reaction Role Panel UI
# -----------------------------
class RRPanel(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Add Reaction Role", style=discord.ButtonStyle.green)
    async def add_rr(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Send the **message ID** you want to attach reaction roles to.",
            ephemeral=True
        )

        def check(m):
            return m.author.id == interaction.user.id and m.channel == interaction.channel

        msg = await self.cog.bot.wait_for("message", check=check)
        msg_id = int(msg.content)

        try:
            target_msg = await interaction.channel.fetch_message(msg_id)
        except:
            return await interaction.followup.send("❌ Invalid message ID.", ephemeral=True)

        await interaction.followup.send("Now send the **emoji**.", ephemeral=True)
        emoji_msg = await self.cog.bot.wait_for("message", check=check)
        emoji = emoji_msg.content

        await interaction.followup.send("Now mention the **role**.", ephemeral=True)
        role_msg = await self.cog.bot.wait_for("message", check=check)
        role = role_msg.role_mentions[0] if role_msg.role_mentions else None

        if role is None:
            return await interaction.followup.send("❌ You must mention a role.", ephemeral=True)

        try:
            await target_msg.add_reaction(emoji)
        except:
            return await interaction.followup.send("❌ I cannot react with that emoji.", ephemeral=True)

        data = self.cog.load_data()
        if str(msg_id) not in data:
            data[str(msg_id)] = {}
        data[str(msg_id)][emoji] = role.id
        self.cog.save_data(data)

        await interaction.followup.send(
            f"✅ Added reaction role:\nEmoji: {emoji}\nRole: {role.name}",
            ephemeral=True
        )

    @discord.ui.button(label="Remove Reaction Role", style=discord.ButtonStyle.red)
    async def remove_rr(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Send the **message ID** to remove reaction roles from.",
            ephemeral=True
        )

        def check(m):
            return m.author.id == interaction.user.id and m.channel == interaction.channel

        msg = await self.cog.bot.wait_for("message", check=check)
        msg_id = msg.content

        data = self.cog.load_data()

        if msg_id not in data:
            return await interaction.followup.send("❌ No reaction roles found for that message.", ephemeral=True)

        del data[msg_id]
        self.cog.save_data(data)

        await interaction.followup.send("🗑 Reaction roles removed.", ephemeral=True)

    @discord.ui.button(label="List Reaction Roles", style=discord.ButtonStyle.blurple)
    async def list_rr(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = self.cog.load_data()

        if not data:
            return await interaction.response.send_message("No reaction roles set.", ephemeral=True)

        embed = discord.Embed(title="📋 Reaction Roles", color=discord.Color.yellow())

        for msg_id, mapping in data.items():
            text = ""
            for emoji, role_id in mapping.items():
                role = interaction.guild.get_role(role_id)
                text += f"{emoji} → {role.name if role else 'Unknown Role'}\n"

            embed.add_field(name=f"Message ID: {msg_id}", value=text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


# -----------------------------
# Setup
# -----------------------------
async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))

