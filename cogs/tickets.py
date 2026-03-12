import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import asyncio

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # CRIAR CONFIGURAÇÃO DE TICKET
    @app_commands.command(name="criarticket", description="Cria um painel de ticket.")
    async def criarticket(self, interaction: discord.Interaction):

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO tickets (guild_id, titulo, descricao, cor, emoji, canal_id, staff_id, imagem)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction.guild.id,
            "Suporte",
            "Clique no botão abaixo para abrir um ticket de suporte.",
            0x3498db,
            "🎫",
            interaction.channel.id,
            None,
            None
        ))

        conn.commit()
        ticket_id = cursor.lastrowid
        conn.close()

        embed = discord.Embed(
            title="Suporte",
            description="Clique no botão abaixo para abrir um ticket de suporte.",
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

    # LISTAR TICKETS
    @app_commands.command(name="listartickets", description="Lista tickets.")
    async def listartickets(self, interaction: discord.Interaction):

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, titulo
        FROM tickets
        WHERE guild_id=?
        """, (interaction.guild.id,))

        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            await interaction.response.send_message("Nenhum ticket criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{t[0]}` - {t[1]}" for t in tickets])

        await interaction.response.send_message(f"**Tickets:**\n{lista}")

    # DELETAR CONFIGURAÇÃO
    @app_commands.command(name="deletarticket", description="Deleta um ticket.")
    async def deletarticket(self, interaction: discord.Interaction, id: int):

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM tickets
        WHERE id=? AND guild_id=?
        """, (id, interaction.guild.id))

        conn.commit()
        conn.close()

        await interaction.response.send_message(f"Ticket `{id}` deletado.")

    # ENVIAR PAINEL
    @app_commands.command(name="enviarticket", description="Envia painel de ticket.")
    async def enviarticket(self, interaction: discord.Interaction, id: int):

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT titulo, descricao, cor, emoji
        FROM tickets
        WHERE id=? AND guild_id=?
        """, (id, interaction.guild.id))

        dados = cursor.fetchone()
        conn.close()

        if not dados:
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=dados[0],
            description=dados[1],
            color=dados[2]
        )

        view = discord.ui.View()

        button = discord.ui.Button(
            label="Abrir Ticket",
            emoji=dados[3],
            style=discord.ButtonStyle.primary,
            custom_id=f"abrir_ticket_{id}"
        )

        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    # EVENTO DOS BOTÕES
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):

        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")

        if not custom_id:
            return

        # ABRIR TICKET
        if custom_id.startswith("abrir_ticket_"):

            ticket_id = int(custom_id.split("_")[-1])

            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()

            cursor.execute("""
            SELECT titulo
            FROM tickets
            WHERE id=? AND guild_id=?
            """, (ticket_id, interaction.guild.id))

            dados = cursor.fetchone()
            conn.close()

            if not dados:
                await interaction.response.send_message(
                    "Configuração não encontrada.",
                    ephemeral=True
                )
                return

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
                f"{interaction.user.mention} abriu um ticket.\nAguarde a equipe.",
                view=view
            )

        # FECHAR TICKET
        if custom_id == "fechar_ticket":

            await interaction.response.send_message(
                "🔒 Fechando ticket em 5 segundos...",
                ephemeral=True
            )

            await asyncio.sleep(5)

            await interaction.channel.delete()


async def setup(bot):
    await bot.add_cog(Tickets(bot))