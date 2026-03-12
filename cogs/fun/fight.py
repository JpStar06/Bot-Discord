import discord
from discord import app_commands
from discord.ext import commands
import random


class ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="fight", description="Lute com outro usuário.")
    async def fight(self, interaction: discord.Interaction, usuario: discord.Member):

        vencedor = random.choice([interaction.user, usuario])

        embed = discord.Embed(
            title="⚔️ Luta!",
            description=f"{interaction.user.mention} lutou contra {usuario.mention}!\n\n🏆 **Vencedor:** {vencedor.mention}",
            color=0xe74c3c
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ball(bot))