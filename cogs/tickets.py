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
        await thread.send(f"{interaction.user.mention} abriu um ticket.\nAguarde a equipe.", view=fechar_view)


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

    tickets = app_commands.Group(name="tickets", description="Sistema de tickets")

    # ================= DB =================

    async def get_conn(self):
        pool = await get_connection()
        return pool.acquire()

<<<<<<< Updated upstream
    # ================= CRIAR =================

    @tickets.command(name="criar")
    @app_commands.checks.has_permissions(administrator=True)
    async def criar(self, interaction: discord.Interaction):

        async with await self.get_conn() as conn:
            ticket_id = await conn.fetchval("""
                INSERT INTO tickets (guild_id, titulo, descricao, cor, emoji, canal_id, staff_id, imagem)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                RETURNING id
=======
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
>>>>>>> Stashed changes
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

        await interaction.response.send_message(f"✅ Ticket criado ID `{ticket_id}`")

    # ================= EDITAR =================

    @tickets.command(name="editar")
    @app_commands.checks.has_permissions(administrator=True)
    async def editar(
        self,
        interaction: discord.Interaction,
        id: int,
        titulo: str = None,
        descricao: str = None,
        cor: int = None,
        imagem: str = None,
        emoji: str = None,
        canal: discord.TextChannel = None,
        staff: discord.Role = None
    ):

        async with await self.get_conn() as conn:

            data = await conn.fetchrow("""
                SELECT * FROM tickets
                WHERE id=$1 AND guild_id=$2
            """, id, interaction.guild.id)

            if not data:
                await interaction.response.send_message("❌ Ticket não encontrado.", ephemeral=True)
                return

            await conn.execute("""
                UPDATE tickets
                SET titulo = COALESCE($1, titulo),
                    descricao = COALESCE($2, descricao),
                    cor = COALESCE($3, cor),
                    imagem = COALESCE($4, imagem),
                    emoji = COALESCE($5, emoji),
                    canal_id = COALESCE($6, canal_id),
                    staff_id = COALESCE($7, staff_id)
                WHERE id=$8
            """,
                titulo,
                descricao,
                cor,
                imagem,
                emoji,
                canal.id if canal else None,
                staff.id if staff else None,
                id
            )

        await interaction.response.send_message("✅ Ticket atualizado!")

    # ================= ENVIAR =================

    @tickets.command(name="enviar")
    async def enviar(self, interaction: discord.Interaction, id: int):

        async with await self.get_conn() as conn:
            data = await conn.fetchrow("""
                SELECT * FROM tickets
                WHERE id=$1 AND guild_id=$2
            """, id, interaction.guild.id)

        if not data:
            await interaction.response.send_message("❌ Ticket não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
<<<<<<< Updated upstream
            title=data["titulo"],
            description=data["descricao"],
            color=data["cor"]
=======
            title="Suporte",
            description="Clique no botão abaixo para abrir um ticket de suporte.",
            color=0x3498db
>>>>>>> Stashed changes
        )
        view = TicketView(ticket_id)
        await interaction.response.send_message(f"Painel criado com ID `{ticket_id}`", embed=embed, view=view)

<<<<<<< Updated upstream
        if data["imagem"]:
            embed.set_image(url=data["imagem"])

        view = discord.ui.View()

        view.add_item(discord.ui.Button(
            label="Abrir Ticket",
            emoji=data["emoji"],
            style=discord.ButtonStyle.primary,
            custom_id=f"abrir_ticket_{id}"
        ))

        canal = interaction.guild.get_channel(data["canal_id"]) or interaction.channel

        await canal.send(embed=embed, view=view)

        await interaction.response.send_message("✅ Painel enviado!", ephemeral=True)

    # ================= LISTAR =================

    @tickets.command(name="listar")
    async def listar(self, interaction: discord.Interaction):

        async with await self.get_conn() as conn:
            tickets = await conn.fetch("""
                SELECT id, titulo FROM tickets
                WHERE guild_id=$1
            """, interaction.guild.id)
=======
    # -------------------- LISTAR TICKETS --------------------
    @tickets.command(name="listar", description="Lista tickets.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listartickets(self, interaction: discord.Interaction):
        conn = await get_connection()
        tickets = await conn.fetch("SELECT id, titulo FROM tickets WHERE guild_id=$1", interaction.guild.id)
        await conn.close()
>>>>>>> Stashed changes

        if not tickets:
            await interaction.response.send_message("Nenhum ticket.", ephemeral=True)
            return

<<<<<<< Updated upstream
        text = "\n".join([f"`{t['id']}` - {t['titulo']}" for t in tickets])

        await interaction.response.send_message(f"📄 **Tickets:**\n{text}")

    # ================= DELETAR =================

    @tickets.command(name="deletar")
    async def deletar(self, interaction: discord.Interaction, id: int):

        async with await self.get_conn() as conn:
            await conn.execute("""
                DELETE FROM tickets
                WHERE id=$1 AND guild_id=$2
            """, id, interaction.guild.id)

        await interaction.response.send_message("🗑️ Ticket deletado.")

    # ================= BOTÕES =================

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):

        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")

        if not custom_id:
            return

        # ===== ABRIR =====
        if custom_id.startswith("abrir_ticket_"):

            ticket_id = int(custom_id.split("_")[-1])

            async with await self.get_conn() as conn:
                data = await conn.fetchrow("SELECT * FROM tickets WHERE id=$1", ticket_id)

            canal = interaction.channel

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            if data["staff_id"]:
                role = interaction.guild.get_role(data["staff_id"])
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)

            thread = await canal.create_thread(
                name=f"ticket-{interaction.user.name}",
                type=discord.ChannelType.private_thread
            )

            await thread.add_user(interaction.user)

            await interaction.response.send_message(
                f"🎫 Ticket criado: {thread.mention}",
                ephemeral=True
            )

            view = discord.ui.View()

            view.add_item(discord.ui.Button(
                label="Fechar Ticket",
                style=discord.ButtonStyle.danger,
                emoji="🔒",
                custom_id="fechar_ticket"
            ))

            await thread.send(
                f"{interaction.user.mention} abriu um ticket.",
                view=view
            )

        # ===== FECHAR =====
        if custom_id == "fechar_ticket":

            await interaction.response.send_message("🔒 Fechando em 3s...", ephemeral=True)

            await asyncio.sleep(3)

            await interaction.channel.delete()

    # ================= ERROS =================

=======
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
>>>>>>> Stashed changes
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Você precisa ser **administrador** para usar esse comando. ta achando que a vida é um murango é?? >:(",
                ephemeral=True
            )


# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Tickets(bot))
