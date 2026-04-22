import discord
from discord import app_commands
from discord.ext import commands
from database import get_connection
from . import services
from . import embeds
from .view import TicketBuilderView

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    async def cog_load(self):
        self.pool = get_connection()

    tickets = app_commands.Group(name="tickets", description="Comandos de tickets")

    # -------------------- CRIAR TICKET  --------------------
    @tickets.command(name="criar", description="cria um ticket padrão")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarticket(self, interaction: discord.Interaction):
        ticket_id = await services.criarticket(interaction.guild.id)

        await interaction.response.send_message(f"ticket criado com ID `{ticket_id}`", embed=embeds.padrao(), ephemeral=True)

    @tickets.command(name="listar", description="lista todos os tickets do server")
    @app_commands.checks.has_permissions(administrator=True)
    async def listartickets(self, interaction: discord.Interaction):
        ticketlist = await services.listarembeds(interaction.guild.id)
        if not ticketlist:
            await interaction.response.send_message(embed=embeds.erro("Nenhum ticket criado."),ephemeral=True)
            return
        
        lista = "\n".join([f"ID `{e['id']}` - {e['title']}" for e in ticketlist])
        await interaction.response.send_message(embed=embeds.lista(lista))

    @tickets.command(name="editar", description="edita tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def builder(self, interaction: discord.Interaction, id: int):
        data = await services.buscar_ticket(interaction.guild.id, id)

        if not data:
            await interaction.response.send_message(embed=embeds.erro("ticket não encontrado."), ephemeral=True)
            return
        view = TicketBuilderView(interaction.user)
         # carregar dados
        view.title = data["title"]
        view.description = data["description"]
        view.color = data["color"]
        view.image = data["image"]

        view.ticket_id = id

        await interaction.response.send_message(embed=view.build_embed(), view=view)

    @tickets.command(name="enviar", description=" envia o ticket para um canal")
    @app_commands.checks.has_permissions(administrator=True)
    async def enviar_ticket(self, interaction: discord.Interaction, id: int, canal: discord.TextChannel):
        data = await services.buscar_ticket(interaction.guild.id, id)
        
        if not data:
            await interaction.response.send_message(embed=embeds.erro("Ticket não encontrado."), ephemeral=True)
            return
        
        embed = discord.Embed(title=data["title"], description=data["description"], color=data["color"])

        if data["image"]:
            embed.set_image(url=data["image"])

        await canal.send(embed=embed)

        await interaction.response.send_message(embed=embeds.acerto(f"✅ ticket `{id}` enviado para {canal.mention}!"))

async def setup(bot):
    await bot.add_cog(Tickets(bot))