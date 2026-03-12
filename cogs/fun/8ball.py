import discord
from discord import app_commands
from discord.ext import commands
import random


class ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="8ball", description="Faça uma pergunta para a bola mágica.")
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

async def setup(bot):
    await bot.add_cog(ball(bot))