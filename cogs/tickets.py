import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from database import get_connection


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tickets = app_commands.Group(name="tickets", description="Comandos de tickets")

    # ================= CRIAR =================
    @tickets.command(name="criar", description="Cria um painel de ticket.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarticket(self, interaction: discord.Interaction):

        pool = await get_connection()

        async with pool.acquire() as conn:
            ticket_id = await conn.fetchval("""
                INSERT INTO tickets (guild_id, titulo, descricao, cor, emoji, canal_id, staff_id, imagem)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                RETURNING id
            """,
                interaction.guild.id,
                "Suporte",
                "Clique no botão abaixo para abrir um ticket.",
                0x3498db,
                "🎫",
                interaction.channel.id,
                None,
                None
            )

        embed = discord.Embed(
            title="Suporte",
            description="Clique no botão abaixo para abrir um ticket.",
            color=0x3498db
        )

        view = discord.ui.View()

        button = discord.ui.Button(
            label="Abrir Ticket",
            emoji="🎫",
            style=discord.ButtonStyle.primary,
            custom_id=f"abrir_ticket_{ticket_id}"
        )

        view.add_item(button)

        await interaction.response.send_message(
            f"Painel criado com ID `{ticket_id}`",
            embed=embed,
            view=view
        )

    # ================= LISTAR =================
    @tickets.command(name="listar", description="Lista tickets.")
    async def listartickets(self, interaction: discord.Interaction):

        pool = await get_connection()

        async with pool.acquire() as conn:
            tickets = await conn.fetch("""
                SELECT id, titulo
                FROM tickets
                WHERE guild_id=$1
            """, interaction.guild.id)

        if not tickets:
            await interaction.response.send_message("Nenhum ticket criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{t['id']}` - {t['titulo']}" for t in tickets])

        await interaction.response.send_message(f"**Tickets:**\n{lista}")

    # ================= DELETAR =================
    @tickets.command(name="deletar", description="Deleta um ticket.")
    async def deletarticket(self, interaction: discord.Interaction, id: int):

        pool = await get_connection()

        async with pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM tickets
                WHERE id=$1 AND guild_id=$2
            """, id, interaction.guild.id)

        await interaction.response.send_message(f"Ticket `{id}` deletado.")

    # ================= ENVIAR =================
    @tickets.command(name="enviar", description="Envia painel.")
    async def enviarticket(self, interaction: discord.Interaction, id: int):

        pool = await get_connection()

        async with pool.acquire() as conn:
            dados = await conn.fetchrow("""
                SELECT titulo, descricao, cor, emoji
                FROM tickets
                WHERE id=$1 AND guild_id=$2
            """, id, interaction.guild.id)

        if not dados:
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=dados["titulo"],
            description=dados["descricao"],
            color=dados["cor"]
        )

        view = discord.ui.View()

        button = discord.ui.Button(
            label="Abrir Ticket",
            emoji=dados["emoji"],
            style=discord.ButtonStyle.primary,
            custom_id=f"abrir_ticket_{id}"
        )

        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    # ================= BOTÕES =================
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):

        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")

        if not custom_id:
            return

        # 🔥 ABRIR TICKET
        if custom_id.startswith("abrir_ticket_"):

            canal = interaction.channel

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

            fechar = discord.ui.Button(
                label="Fechar Ticket",
                style=discord.ButtonStyle.danger,
                emoji="🔒",
                custom_id="fechar_ticket"
            )

            view.add_item(fechar)

            await thread.send(
                f"{interaction.user.mention} abriu um ticket.",
                view=view
            )

        # 🔥 FECHAR
        if custom_id == "fechar_ticket":

            await interaction.response.send_message(
                "🔒 Fechando em 5s...",
                ephemeral=True
            )

            await asyncio.sleep(5)

            await interaction.channel.delete()

    # ================= ERROS =================
    async def cog_app_command_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Você precisa ser admin 😏",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Tickets(bot))