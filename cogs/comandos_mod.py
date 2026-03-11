import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class Mods(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @app_commands.command(name="banir", description="Bane um usuário do servidor.")
        @app_commands.describe(user="Usuário a ser banido", reason="Motivo do banimento")
        async def banir(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
            if user.top_role >= interaction.user.top_role:
                await interaction.response.send_message("Você não pode banir esse usuário.",ephemeral=True)
                return
            try:
                await user.send(f"Você foi banido do servidor **{interaction.guild.name}**. Motivo: {reason if reason else 'Sem motivo especificado.'}")
            except:
                pass
            await user.ban(reason=reason)
            await interaction.response.send_message(f"Usuário {user.mention} banido com sucesso. Motivo: {reason if reason else 'Sem motivo especificado.'}")

        @app_commands.command(name="kickar", description="Kicka um usuário do servidor.")
        @app_commands.describe(user="Usuário a ser kickado", reason="Motivo do kick")
        async def kickar(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
            if user.top_role >= interaction.user.top_role:
                await interaction.response.send_message("Você não pode kickar esse usuário.",ephemeral=True)
                return
            try:
                await user.send(f"Você foi kickado do servidor **{interaction.guild.name}**. Motivo: {reason if reason else 'Sem motivo especificado.'}")
            except:
                pass
            await user.kick(reason=reason)
            await interaction.response.send_message(f"Usuário {user.mention} kickado com sucesso. Motivo: {reason if reason else 'Sem motivo especificado.'}")

        @app_commands.command(name="muter", description="Mutar um usuário no servidor.")
        @app_commands.describe(user="Usuário a ser mutado", reason="Motivo da mutação")
        async def muter(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
            if user.top_role >= interaction.user.top_role:
                await interaction.response.send_message("Você não pode mutar esse usuário.",ephemeral=True)
                return
            try:
                await user.send(f"Você foi mutado no servidor **{interaction.guild.name}**. Motivo: {reason if reason else 'Sem motivo especificado.'}")
            except:
                pass
            await user.timeout(duration=discord.timedelta(minutes=10), reason=reason)
            await interaction.response.send_message(f"Usuário {user.mention} mutado com sucesso. Motivo: {reason if reason else 'Sem motivo especificado.'}")

        @app_commands.command(name="unmuter", description="Desmutar um usuário no servidor.")
        @app_commands.describe(user="Usuário a ser desmutado", reason="Motivo da desmutação")
        async def unmuter(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
            if user.top_role >= interaction.user.top_role:
                await interaction.response.send_message("Você não pode desmutar esse usuário.",ephemeral=True)
                return
            try:
                await user.send(f"Você foi desmutado no servidor **{interaction.guild.name}**. Motivo: {reason if reason else 'Sem motivo especificado.'}")
            except:
                pass
            await user.timeout(duration=discord.timedelta(minutes=0), reason=reason)
            await interaction.response.send_message(f"Usuário {user.mention} desmutado com sucesso. Motivo: {reason if reason else 'Sem motivo especificado.'}")

async def setup(bot):
    await bot.add_cog(Mods(bot))