# cogs/tickets.py
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# -------------------- CONEXÃO ASYNC --------------------
async def get_connection():
    return await asyncpg.connect(DATABASE_URL)


# -------------------- VIEW PARA ABRIR TICKETS --------------------
class TicketView(discord.ui.View):
    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)  # Persistente
        self.ticket_id = ticket_id

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="abrir_ticket")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = await get_connection()
        dados = await conn.fetchrow(
            "SELECT titulo FROM tickets WHERE id=$1 AND guild_id=$2",
            self.ticket_id, interaction.guild.id
        )
        await conn.close()

        if not dados:
            await interaction.response.send_message("Configuração não encontrada.", ephemeral=True)
            return

        try:
            thread = await interaction.channel.create_thread(
                name=f"ticket-{interaction.user.name}",
                type=discord.ChannelType.private_thread
            )
            await thread.add_user(interaction.user)
        except Exception as e:
            await interaction.response.send_message(f"Não foi possível criar o ticket: {e}", ephemeral=True)
            return

        await interaction.response.send_message(f"🎫 Ticket criado: {thread.mention}", ephemeral=True)

        fechar_view = FecharTicketView()

        embed = diacord.Embed(
            title="**ESPERE SER ATENDIDO**",
            description=(
                "Nossa equipe de moderadores pode estar ocupada no momento.\n"
                "Envie somente o necessário e não marque os moderadores."
            ),
            color=discord.Color.red()
        )
        
        await thread.send(f"{interaction.user.mention} abriu um ticket.\nAguarde a equipe.", embed=embed, view=fechar_view)


# -------------------- VIEW PARA FECHAR TICKETS --------------------
class FecharTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="fechar_ticket")
    async def fechar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Fechando ticket em 5 segundos...", ephemeral=True)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass


# -------------------- COG --------------------
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tickets = app_commands.Group(name="tickets", description="Comandos de tickets")

    # -------------------- CRIAR CONFIGURAÇÃO --------------------
    @tickets.command(name="criar", description="Cria um painel de ticket.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarticket(self, interaction: discord.Interaction):
        conn = await get_connection()
        ticket_id = await conn.fetchval(
            """
            INSERT INTO tickets (guild_id, titulo, descricao, cor, emoji, canal_id, staff_id, imagem)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            interaction.guild.id,
            "Suporte",
            "Clique no botão abaixo para abrir um ticket de suporte.",
            0x3498db,
            "🎫",
            interaction.channel.id,
            None,
            None
        )
        await conn.close()

        embed = discord.Embed(
            title="Suporte",
            description="Clique no botão abaixo para abrir um ticket de suporte.",
            color=0x3498db
        )
        view = TicketView(ticket_id)
        await interaction.response.send_message(f"Painel criado com ID `{ticket_id}`", embed=embed, view=view)

    # -------------------- LISTAR TICKETS --------------------
    @tickets.command(name="listar", description="Lista tickets.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listartickets(self, interaction: discord.Interaction):
        conn = await get_connection()
        tickets = await conn.fetch("SELECT id, titulo FROM tickets WHERE guild_id=$1", interaction.guild.id)
        await conn.close()

        if not tickets:
            await interaction.response.send_message("Nenhum ticket criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{t['id']}` - {t['titulo']}" for t in tickets])
        await interaction.response.send_message(f"**Tickets:**\n{lista}")

    # -------------------- DELETAR CONFIGURAÇÃO --------------------
    @tickets.command(name="deletar", description="Deleta um ticket.")
    @app_commands.checks.has_permissions(administrator=True)
    async def deletarticket(self, interaction: discord.Interaction, id: int):
        conn = await get_connection()
        await conn.execute("DELETE FROM tickets WHERE id=$1 AND guild_id=$2", id, interaction.guild.id)
        await conn.close()
        await interaction.response.send_message(f"Ticket `{id}` deletado.")

    # -------------------- ENVIAR PAINEL --------------------
    @tickets.command(name="enviar", description="Envia painel de ticket.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enviarticket(self, interaction: discord.Interaction, id: int):
        conn = await get_connection()
        dados = await conn.fetchrow(
            "SELECT titulo, descricao, cor, emoji FROM tickets WHERE id=$1 AND guild_id=$2",
            id, interaction.guild.id
        )
        await conn.close()

        if not dados:
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(title=dados['titulo'], description=dados['descricao'], color=dados['cor'])
        view = TicketView(id)
        await interaction.response.send_message(embed=embed, view=view)

    # -------------------- ERROS --------------------
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Você precisa ser **administrador** para usar esse comando. ta achando que a vida é um murango é?? >:(",
                ephemeral=True
            )


# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Tickets(bot))
