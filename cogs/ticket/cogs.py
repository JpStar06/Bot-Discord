import discord
from discord import app_commands
from discord.ext import commands
from cogs.ticket.services import TicketService
from cogs.ticket.embeds import TicketEmbed, acerto
from cogs.ticket.view import EditPanelView, EditTopicView, TicketView


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

    # ---------- EDITAR PAINEL ----------
    @tickets.command(name="editar-painel", description="Edita o painel do ticket")
    async def editar(self, interaction: discord.Interaction, id: int):

        data = await TicketService.get_ticket(interaction.guild.id, id)

        if not data:
            await interaction.response.send_message(
                "❌ Ticket não encontrado.",
                ephemeral=True
            )
            return

        view = EditPanelView(data, id, interaction.guild.id, interaction.user)

        await interaction.response.send_message(
            content="👀 Pré-visualização do painel:",
            embed=view.build_embed(),
            view=view,
            ephemeral=True
        )

    # ---------- EDITAR TÓPICO ----------
    @tickets.command(name="editar-topico", description="Edita o embed do tópico do ticket")
    async def editar_topico(self, interaction: discord.Interaction, id: int):

        data = await TicketService.get_ticket(interaction.guild.id, id)

        if not data:
            await interaction.response.send_message(
                "❌ Ticket não encontrado.",
                ephemeral=True
            )
            return

        view = EditTopicView(data, id, interaction.guild.id, interaction.user)

        await interaction.response.send_message(
            content="👀 Pré-visualização do tópico:",
            embed=view.build_embed(),
            view=view,
            ephemeral=True
        )

    # ---------- ENVIAR ----------
    @tickets.command(name="enviar", description="Envia painel de ticket")
    async def enviar(self, interaction: discord.Interaction, id: int, canal: discord.TextChannel):

        data = await TicketService.get_ticket(
            interaction.guild.id,
            id
        )

        if not data:
            await interaction.response.send_message(
                "❌ Ticket não encontrado.",
                ephemeral=True
            )
            return

        embed = TicketEmbed.painel(data)

        await canal.send(embed=embed, view=TicketView(id))

        await interaction.response.send_message(
            embed=acerto(f"✅ Ticket `{id}` enviado para {canal.mention}!")
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
