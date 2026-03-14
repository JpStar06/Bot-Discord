import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from database import get_connection


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tickets = app_commands.Group(name="tickets", description="Comandos de tickets")

    # CRIAR CONFIGURAÇÃO DE TICKET
    @tickets.command(name="criar", description="Cria um painel de ticket.")
    @app_commands.default_permissions(administrator=True)
    async def criarticket(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO tickets (guild_id, titulo, descricao, cor, emoji, canal_id, staff_id, imagem)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
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

        ticket_id = cursor.fetchone()[0]

        conn.commit()
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
    @tickets.command(name="listar", description="Lista tickets.")
    @app_commands.default_permissions(administrator=True)
    async def listartickets(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, titulo
        FROM tickets
        WHERE guild_id=%s
        """, (interaction.guild.id,))

        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            await interaction.response.send_message("Nenhum ticket criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{t[0]}` - {t[1]}" for t in tickets])

        await interaction.response.send_message(f"**Tickets:**\n{lista}")

    # DELETAR CONFIGURAÇÃO
    @tickets.command(name="deletar", description="Deleta um ticket.")
    @app_commands.default_permissions(administrator=True)

    async def deletarticket(self, interaction: discord.Interaction, id: int):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM tickets
        WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id))

        conn.commit()
        conn.close()

        await interaction.response.send_message(f"Ticket `{id}` deletado.")

    # ENVIAR PAINEL
    @tickets.command(name="enviar", description="Envia painel de ticket.")
    @app_commands.default_permissions(administrator=True)

    async def enviarticket(self, interaction: discord.Interaction, id: int):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT titulo, descricao, cor, emoji
        FROM tickets
        WHERE id=%s AND guild_id=%s
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
    
    @tickets.command(name="editar", description="Edita a configuração de um ticket.")
    @app_commands.describe(
        id="ID do ticket",
        titulo="Novo título",
        descricao="Nova descrição",
        cor="Nova cor em HEX (ex: FF0000)",
        emoji="Novo emoji do botão",
        imagem="URL da imagem",
        canal="Canal onde o ticket será criado",
        staff="Cargo da equipe de suporte"
    )
    @app_commands.default_permissions(administrator=True)

    async def editarticket(
        self,
        interaction: discord.Interaction,
        id: int,
        titulo: str = None,
        descricao: str = None,
        cor: str = None,
        emoji: str = None,
        imagem: str = None,
        canal: discord.TextChannel = None,
        staff: discord.Role = None
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT titulo, descricao, cor, emoji, canal_id, staff_id, imagem
        FROM tickets
        WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id))

        ticket = cursor.fetchone()

        if not ticket:
            await interaction.response.send_message(
                "Ticket não encontrado.",
                ephemeral=True
            )
            conn.close()
            return

        novo_titulo = titulo if titulo else ticket[0]
        nova_descricao = descricao if descricao else ticket[1]
        nova_cor = int(cor, 16) if cor else ticket[2]
        novo_emoji = emoji if emoji else ticket[3]
        novo_canal = canal.id if canal else ticket[4]
        novo_staff = staff.id if staff else ticket[5]
        nova_imagem = imagem if imagem else ticket[6]

        cursor.execute("""
        UPDATE tickets
        SET titulo=%s,
            descricao=%s,
            cor=%s,
            emoji=%s,
            canal_id=%s,
            staff_id=%s,
            imagem=%s
        WHERE id=%s AND guild_id=%s
        """, (
            novo_titulo,
            nova_descricao,
            nova_cor,
            novo_emoji,
            novo_canal,
            novo_staff,
            nova_imagem,
            id,
            interaction.guild.id
        ))


        conn.commit()
        conn.close()

        embed = discord.Embed(
            title=novo_titulo,
            description=nova_descricao,
            color=nova_cor
        )

        if nova_imagem:
            embed.set_image(url=nova_imagem)

        await interaction.response.send_message(
            f"✅ Ticket `{id}` atualizado com sucesso.",
            embed=embed
        )

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

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            SELECT titulo
            FROM tickets
            WHERE id=%s AND guild_id=%s
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