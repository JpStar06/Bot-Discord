import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Mods(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    adm = app_commands.Group(name="adm", description="Comandos de adm")

    @adm.command(name="banir", description="Bane um usuário do servidor.")
    @app_commands.describe(user="Usuário a ser banido", reason="Motivo do banimento")
    @app_commands.default_permissions(administrator=True)
    async def banir(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):

        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("Você não pode banir esse usuário.", ephemeral=True)
            return

        try:
            await user.send(f"Você foi banido do servidor **{interaction.guild.name}**.\nMotivo: {reason or 'Sem motivo.'}")
        except:
            pass

        await user.ban(reason=reason)

        await interaction.response.send_message(
            f"🔨 Usuário {user.mention} banido.\nMotivo: {reason or 'Sem motivo.'}"
        )

    @adm.command(name="kickar", description="Kicka um usuário do servidor.")
    @app_commands.describe(user="Usuário a ser kickado", reason="Motivo do kick")
    @app_commands.default_permissions(administrator=True)
    async def kickar(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):

        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("Você não pode kickar esse usuário.", ephemeral=True)
            return

        try:
            await user.send(f"Você foi kickado do servidor **{interaction.guild.name}**.\nMotivo: {reason or 'Sem motivo.'}")
        except:
            pass

        await user.kick(reason=reason)

        await interaction.response.send_message(
            f"👢 Usuário {user.mention} kickado.\nMotivo: {reason or 'Sem motivo.'}"
        )

    @adm.command(name="mutar", description="Muta um usuário.")
    @app_commands.describe(user="Usuário a ser mutado", minutos="Tempo do mute")
    @app_commands.default_permissions(administrator=True)
    async def mutar(self, interaction: discord.Interaction, user: discord.Member, minutos: int):

        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("Você não pode mutar esse usuário.", ephemeral=True)
            return

        tempo = timedelta(minutes=minutos)

        await user.timeout(tempo)

        await interaction.response.send_message(
            f"🔇 {user.mention} foi mutado por **{minutos} minutos**."
        )

    @adm.command(name="desmutar", description="Remove o mute de um usuário.")
    @app_commands.describe(user="Usuário a ser desmutado")
    @app_commands.default_permissions(administrator=True)
    async def desmutar(self, interaction: discord.Interaction, user: discord.Member):

        await user.timeout(None)

        await interaction.response.send_message(
            f"🔊 {user.mention} foi desmutado."
        )


async def setup(bot):
    await bot.add_cog(Mods(bot))