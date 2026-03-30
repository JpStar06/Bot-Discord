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
            color=discord.Color.dark_embed()
        )

        await interaction.response.send_message(embed=embed)


    @play.command(name="fight", description="Lute com outro usuário.")
    async def fight(self, interaction: discord.Interaction, usuario: discord.Member):

        # evita lutar contra si mesmo
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "🤨 Você não pode lutar contra você mesmo!",
                ephemeral=True
            )
            return

        vencedor = random.choice([interaction.user, usuario])

        embed = discord.Embed(
            title="⚔️ Luta!",
            description=(
                f"{interaction.user.mention} lutou contra {usuario.mention}!\n\n"
                f"🏆 **Vencedor:** {vencedor.mention}"
            ),
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Misc(bot))