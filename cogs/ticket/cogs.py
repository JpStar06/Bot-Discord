import discord
from discord import app_commands
from discord.ext import commands
from cogs.ticket.services import TicketService
from cogs.ticket.embeds import TicketEmbed, acerto
from cogs.ticket.view import EditPanelView
from cogs.ticket.modals import EditPanelModal
from cogs.ticket.modals import EditTopicModal
from cogs.ticket.view import TicketView
from cogs.ticket.embeds import TicketEmbed
from cogs.ticket.services import TicketService


class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    tickets = app_commands.Group(name="tickets", description="Sistema de tickets")

    # ---------- CRIAR ----------
    @tickets.command(name="criar")
    async def criar(self, interaction: discord.Interaction):

        ticket_id = await TicketService.create_ticket(
            interaction.guild.id,
            interaction.channel.id
        )

        await interaction.response.send_message(f"✅ Ticket criado ID `{ticket_id}`")

    # ---------- EDITAR (AGORA COM MODAL) ----------
    @tickets.command(name="editar-painel")
    async def editar(self, interaction: discord.Interaction, id: int):

        data = await TicketService.get_ticket(interaction.guild.id, id)

        if not data:
            await interaction.response.send_message(
                "Ticket não encontrado.",
                ephemeral=True
            )
            return

        modal = EditPanelModal(
            data,
            id,
            interaction.guild.id
        )

        await interaction.response.send_modal(modal)

    # ---------- ENVIAR ----------
    @tickets.command(name="enviar", description="Envia painel de ticket")
    async def enviar(self, interaction: discord.Interaction, id: int, canal: discord.TextChannel):

        data = await TicketService.get_ticket(
            interaction.guild.id,
            id
        )

        if not data:
            await interaction.response.send_message(
                "Ticket não encontrado.",
                ephemeral=True
            )
            return

        embed = TicketEmbed.painel(data)

        await canal.send(embed=embed, view=TicketView(id))

        await interaction.response.send_message(embed=acerto(f"✅ Ticket `{id}` enviado para {canal.mention}!"))
    
    @tickets.command(name="editar-topico", description="Edita o embed do tópico do ticket")
    async def editar_topico(self, interaction: discord.Interaction, id: int):

        data = await TicketService.get_ticket(
            interaction.guild.id,
            id
        )

        if not data:
            await interaction.response.send_message(
                "Ticket não encontrado.",
                ephemeral=True
            )
            return

        modal = EditTopicModal(
            data,
            id,
            interaction.guild.id
        )

        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Tickets(bot))