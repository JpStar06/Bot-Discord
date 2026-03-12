import discord
from discord.ext import commands
from discord import app_commands

from services.moderation_service import ban_member, kick_member, mute_member


class Moderation(commands.Cog):

    mod = app_commands.Group(name="mod", description="Comandos de moderação")

    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.mod)


    @mod.command(name="ban", description="Banir um membro")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Sem motivo"):

        await ban_member(interaction.guild, member, reason)

        await interaction.response.send_message(
            f"{member.mention} foi banido.\nMotivo: {reason}"
        )


    @mod.command(name="kick", description="Expulsar um membro")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Sem motivo"):

        await kick_member(member, reason)

        await interaction.response.send_message(
            f"{member.mention} foi expulso.\nMotivo: {reason}"
        )


    @mod.command(name="mute", description="Mutar um membro")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutos: int, reason: str = "Sem motivo"):

        await mute_member(member, minutos, reason)

        await interaction.response.send_message(
            f"{member.mention} foi mutado por {minutos} minutos.\nMotivo: {reason}"
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))