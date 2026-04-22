import discord
from discord.ext import commands
from discord import app_commands
from cogs.ticket.view import EditPanelView, TicketView
from cogs.ticket.embeds import TicketEmbed

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    tickets = app_commands.Group(name="tickets", description="Sistema de tickets")

    @tickets.command(name="editar")
    async def editar(self, interaction: discord.Interaction, id: int):

        data = {
            "titulo": "Suporte",
            "descricao": "Clique abaixo",
            "cor": 0x3498db,
            "imagem": None,
            "staff_id": None
        }

        embed = TicketEmbed.painel(data)

        await interaction.response.send_message(
            embed=embed,
            view=EditPanelView(data, id, interaction.guild.id),
            ephemeral=True
        )

    @tickets.command(name="enviar")
    async def enviar(self, interaction: discord.Interaction, id: int):

        data = {
            "titulo": "Suporte",
            "descricao": "Clique para abrir",
            "cor": 0x3498db
        }

        embed = TicketEmbed.painel(data)

        await interaction.response.send_message(
            embed=embed,
            view=TicketView(id)
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))