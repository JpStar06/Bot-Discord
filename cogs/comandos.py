import discord
from discord import app_commands
from discord.ext import commands
from database import get_connection
import datetime


class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    embed = app_commands.Group(name="embeds", description="Comandos de embeds")

    # CRIAR EMBED
    @embed.command(name="criar", description="Cria um embed padrão.")
    async def criarembed(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO embeds (guild_id, title, description, color, image)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """, (
            interaction.guild.id,
            "Título do Embed",
            "Descrição padrão",
            0x3498db,
            None
        ))

        embed_id = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="Título do Embed",
            description="Descrição padrão",
            color=0x3498db
        )

        await interaction.response.send_message(
            f"Embed criado com ID `{embed_id}`",
            embed=embed
        )


    # EDITAR EMBED
    @embed.command(name="editar", description="Edita um embed.")
    async def editarembed(
        self,
        interaction: discord.Interaction,
        id: int,
        novo_titulo: str,
        novo_descricao: str = None,
        nova_cor: int = None,
        imagem_url: str = None
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT title, description, color, image FROM embeds WHERE id=%s AND guild_id=%s",
            (id, interaction.guild.id)
        )

        embed_data = cursor.fetchone()

        if not embed_data:
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            conn.close()
            return

        title = novo_titulo
        description = novo_descricao if novo_descricao else embed_data[1]
        color = nova_cor if nova_cor else embed_data[2]
        image = imagem_url if imagem_url else embed_data[3]

        cursor.execute("""
        UPDATE embeds
        SET title=%s, description=%s, color=%s, image=%s
        WHERE id=%s AND guild_id=%s
        """, (title, description, color, image, id, interaction.guild.id))

        conn.commit()
        conn.close()

        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        if image:
            embed.set_image(url=image)

        await interaction.response.send_message("Embed atualizado:", embed=embed)


    # LISTAR EMBEDS
    @embed.command(name="listar", description="Lista os embeds.")
    async def listarembeds(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title FROM embeds WHERE guild_id=%s",
            (interaction.guild.id,)
        )

        embeds = cursor.fetchall()
        conn.close()

        if not embeds:
            await interaction.response.send_message("Nenhum embed criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{e[0]}` - {e[1]}" for e in embeds])

        await interaction.response.send_message(f"**Embeds:**\n{lista}")


    # DELETAR EMBED
    @embed.command(name="deletar", description="Deleta um embed.")
    async def deletarembed(self, interaction: discord.Interaction, id: int):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM embeds WHERE id=%s AND guild_id=%s",
            (id, interaction.guild.id)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(f"Embed `{id}` deletado.")


    # ENVIAR EMBED
    @embed.command(name="enviar", description="Envia um embed.")
    async def enviarembed(self, interaction: discord.Interaction, id: int):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT title, description, color, image
        FROM embeds
        WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id))

        resultado = cursor.fetchone()
        conn.close()

        if not resultado:
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=resultado[0],
            description=resultado[1],
            color=resultado[2]
        )

        if resultado[3]:
            embed.set_image(url=resultado[3])

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="recado-criar", description="Agenda um recado diário")
    @app_commands.describe(embed_id="ID do embed", horario="Horário (HH:MM)", canal="Canal onde o recado será enviado")
    async def criar_recado(self, interaction: discord.Interaction, embed_id: int, horario: str, canal: discord.TextChannel):

        try:
            datetime.datetime.strptime(horario, "%H:%M")
        except ValueError:
            await interaction.response.send_message(
                "❌ Horário inválido. Use o formato `HH:MM` (ex: 12:30).",
                ephemeral=True
            )
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO reminders (guild_id, channel_id, embed_id, horario)
        VALUES (%s, %s, %s, %s)
        """, (
            interaction.guild.id,
            canal.id,
            embed_id,
            horario
        ))

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ Recado agendado para **{horario}** todos os dias."
        )

    @app_commands.command(name="recados-list", description="Lista os recados agendados")
    async def recados(self, interaction: discord.Interaction):
            
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, embed_id, horario, channel_id
        FROM reminders
        WHERE guild_id=%s
        ORDER BY horario
        """, (interaction.guild.id,))

        recados = cursor.fetchall()
        conn.close()

        if not recados:
            await interaction.response.send_message(
                "Nenhum recado agendado.",
                ephemeral=True
            )
            return

        texto = ""

        for r in recados:
            rid, embed_id, horario, channel_id = r
            texto += f"ID `{rid}` • Embed `{embed_id}` • {horario} • <#{channel_id}>\n"

        embed = discord.Embed(
            title="📢 Recados agendados",
            description=texto,
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="recado-deletar", description="Deleta um recado")
    async def recado_deletar(self, interaction: discord.Interaction, id: int):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM reminders
        WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id))

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🗑️ Recado `{id}` deletado."
        )

    @app_commands.command(name="recado-editar", description="Edita um recado")
    async def recado_editar(
        self,
        interaction: discord.Interaction,
        id: int,
        novo_horario: str = None,
        novo_embed: int = None
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT embed_id, horario
        FROM reminders
        WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id))

        recado = cursor.fetchone()

        if not recado:
            await interaction.response.send_message(
                "Recado não encontrado.",
                ephemeral=True
            )
            conn.close()
            return

        embed_id = novo_embed if novo_embed else recado[0]
        horario = novo_horario if novo_horario else recado[1]

        cursor.execute("""
        UPDATE reminders
        SET embed_id=%s, horario=%s
        WHERE id=%s AND guild_id=%s
        """, (embed_id, horario, id, interaction.guild.id))

        conn.commit()
        conn.close()

        await interaction.response.send_message(
                f"✅ Recado `{id}` atualizado para **{horario}**."
            )

async def setup(bot):
    await bot.add_cog(Comandos(bot))