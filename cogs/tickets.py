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


# -------------------- CONEXÃO --------------------
async def get_connection():
    return await asyncpg.connect(DATABASE_URL)


# -------------------- VIEW ABRIR TICKET --------------------
class TicketView(discord.ui.View):
    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="abrir_ticket")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)  # evita timeout

        conn = await get_connection()

        # 🔥 pega tudo de uma vez
        dados = await conn.fetchrow(
            """
            SELECT 
                titulo,
                titulo_cliente, descricao_cliente, cor_cliente, imagem_cliente
            FROM tickets 
            WHERE id=$1 AND guild_id=$2
            """,
            self.ticket_id,
            interaction.guild.id
        )

        if not dados:
            await interaction.followup.send("Configuração não encontrada.", ephemeral=True)
            await conn.close()
            return

        # cria thread
        try:
            thread = await interaction.channel.create_thread(
                name=f"ticket-{interaction.user.name}",
                type=discord.ChannelType.private_thread
            )
            await thread.add_user(interaction.user)
        except Exception as e:
            await interaction.followup.send(f"Erro ao criar ticket: {e}", ephemeral=True)
            await conn.close()
            return

        # embed do cliente
        embed = discord.Embed(
            title=dados["titulo_cliente"] or "Ticket",
            description=dados["descricao_cliente"] or "Aguarde atendimento",
            color=dados["cor_cliente"] or 0xFF0000
        )

        if dados["imagem_cliente"]:
            embed.set_image(url=dados["imagem_cliente"])

        # envia no tópico
        await thread.send(
            content=f"{interaction.user.mention}",
            embed=embed,
            view=FecharTicketView()
        )

        await interaction.followup.send(f"🎫 Ticket criado: {thread.mention}", ephemeral=True)

        await conn.close()


# -------------------- VIEW FECHAR --------------------
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

    # -------------------- CRIAR --------------------
    @tickets.command(name="criar", description="Cria um painel de ticket.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarticket(self, interaction: discord.Interaction):

        conn = await get_connection()

        ticket_id = await conn.fetchval(
            """
            INSERT INTO tickets (
                guild_id, titulo, descricao, cor, emoji, canal_id, staff_id, imagem,
                titulo_cliente, descricao_cliente, cor_cliente, imagem_cliente
            )
            VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8,
                $9, $10, $11, $12
            )
            RETURNING id
            """,
            interaction.guild.id,
            "Suporte",
            "Clique no botão abaixo para abrir um ticket de suporte.",
            0x3498db,
            "🎫",
            interaction.channel.id,
            None,
            None,

            # cliente
            "**ESPERE SER ATENDIDO**",
            "Nossa equipe pode estar ocupada.\nEnvie apenas o necessário.",
            0xFF0000,
            None
        )

        await conn.close()

        embed = discord.Embed(
            title="Suporte",
            description="Clique no botão abaixo para abrir um ticket.",
            color=0x3498db
        )

        await interaction.response.send_message(
            content=f"Painel criado (ID `{ticket_id}`)",
            embed=embed,
            view=TicketView(ticket_id)
        )
    #---------------------EDITAR PAINEL---------------------
    @tickets.command(name="editar-painel", description="Edita o painel principal do ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def editarticket(self, interaction: discord.Interaction, id: int, novo_titulo: str = None, novo_descricao: str = None, nova_cor: int = None, imagem_url: str = None):
        async with self.pool.acquire() as conn:
            ticket_data = await conn.fetchrow("SELECT title, description, color, image FROM tickets WHERE id=$1, guild_id=$2", id, interaction.guild.id)
        if not ticket_data:
            await interaction.reponse.send_message("Ticket não encontrado.", ephemeral=True)
            return
        
        title = novo_titulo or ticket_data["title"]
        description = novo_descricao or ticket_data["description"]
        color = nova_cor or ticket_data["color"]
        image = imagem_url or ticket_data["image"]

        await conn.execute("""
            UPDATE tickets SET title=$1, description=$2, color=$3, image=$4
            WHERE id=$5 AND guild_id=$6
        """, title, description, color, image, id, interaction.guild_id)

        embed = discord.Embed(title=title, description=description, color=color)
        if image:
            embed.set_image(url=image)
        await interaction.response.send_message("Embed atualizado:", embed=embed)

    #---------------------DELETAR--------------------
    @tickets.command(name="deletar", description="Deleta um ticket.")
    @app_commands.checks.has_permissions(administrator=True)
    async def deletarticket(self, interaction: discord.Interaction, id: int):
        conn = await get_connection()
        await conn.execute(
            "DELETE FROM tickets WHERE id=$1 AND guild_id=$2",
            id,
            interaction.guild.id
        )
        await conn.close()
        await interaction.response.send_message(f"Embed `{id}` deletado.")
    # -------------------- LISTAR --------------------
    @tickets.command(name="listar", description="Lista tickets.")
    async def listartickets(self, interaction: discord.Interaction):

        conn = await get_connection()
        tickets = await conn.fetch(
            "SELECT id, titulo FROM tickets WHERE guild_id=$1",
            interaction.guild.id
        )
        await conn.close()

        if not tickets:
            await interaction.response.send_message("Nenhum ticket criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{t['id']}` - {t['titulo']}" for t in tickets])

        await interaction.response.send_message(f"**Tickets:**\n{lista}")

    # -------------------- ENVIAR --------------------
    @tickets.command(name="enviar", description="Envia painel de ticket.")
    async def enviarticket(self, interaction: discord.Interaction, id: int):

        conn = await get_connection()

        dados = await conn.fetchrow(
            "SELECT titulo, descricao, cor FROM tickets WHERE id=$1 AND guild_id=$2",
            id,
            interaction.guild.id
        )

        await conn.close()

        if not dados:
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=dados["titulo"],
            description=dados["descricao"],
            color=dados["cor"]
        )

        await interaction.response.send_message(
            embed=embed,
            view=TicketView(id)
        )


# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Tickets(bot))