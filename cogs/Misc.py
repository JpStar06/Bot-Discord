import discord
from discord import app_commands
from discord.ext import commands
import random


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    play = app_commands.Group(name="play", description="Comandos de mini-games")

    @play.command(name="8ball", description="Faça uma pergunta para a bola mágica.")
    async def eightball(self, interaction: discord.Interaction, pergunta: str):

        respostas = [
            "Sim.",
            "Não.",
            "Talvez.",
            "Com certeza.",
            "Pergunte novamente depois.",
            "Muito improvável.",
            "Definitivamente."
        ]

        resposta = random.choice(respostas)

        embed = discord.Embed(
            title="🎱 8Ball",
            description=f"**Pergunta:** {pergunta}\n**Resposta:** {resposta}",
            color=0x2f3136
        )

        await interaction.response.send_message(embed=embed)


    @play.command(name="fight", description="Lute com outro usuário.")
    async def fight(self, interaction: discord.Interaction, usuario: discord.Member):

        vencedor = random.choice([interaction.user, usuario])

        embed = discord.Embed(
            title="⚔️ Luta!",
            description=f"{interaction.user.mention} lutou contra {usuario.mention}!\n\n🏆 **Vencedor:** {vencedor.mention}",
            color=0xe74c3c
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Misc(bot))
