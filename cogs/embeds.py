import discord
from discord import app_commands
from discord.ext import commands
from database import get_connection
import datetime


class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    embed = app_commands.Group(name="embeds", description="Comandos de embeds")
    recado = app_commands.Group(name="recado", description="Comandos de recados")

    # ========================
    # UTIL
    # ========================
    def db_execute(self, query, params=(), fetchone=False, fetchall=False):
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)

                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()

                conn.commit()

    # ========================
    # EMBEDS
    # ========================

    @embed.command(name="criar", description="Cria um embed padrão.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarembed(self, interaction: discord.Interaction):

        result = self.db_execute("""
            INSERT INTO embeds (guild_id, title, description, color, image)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            interaction.guild.id,
            "Título do Embed",
            "Descrição padrão",
            0x3498db,
            None
        ), fetchone=True)

        embed_id = result[0]

        embed = discord.Embed(
            title="Título do Embed",
            description="Descrição padrão",
            color=0x3498db
        )

        await interaction.response.send_message(
            f"✅ Embed criado com ID `{embed_id}`",
            embed=embed
        )

    @embed.command(name="editar", description="Edita um embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def editarembed(
        self,
        interaction: discord.Interaction,
        id: int,
        novo_titulo: str,
        novo_descricao: str = None,
        nova_cor: int = None,
        imagem_url: str = None
    ):

        data = self.db_execute(
            "SELECT title, description, color, image FROM embeds WHERE id=%s AND guild_id=%s",
            (id, interaction.guild.id),
            fetchone=True
        )

        if not data:
            await interaction.response.send_message("❌ Embed não encontrado.", ephemeral=True)
            return

        title = novo_titulo
        description = novo_descricao or data[1]
        color = nova_cor or data[2]
        image = imagem_url or data[3]

        self.db_execute("""
            UPDATE embeds
            SET title=%s, description=%s, color=%s, image=%s
            WHERE id=%s AND guild_id=%s
        """, (title, description, color, image, id, interaction.guild.id))

        embed = discord.Embed(title=title, description=description, color=color)

        if image:
            embed.set_image(url=image)

        await interaction.response.send_message("✅ Embed atualizado:", embed=embed)

    @embed.command(name="listar", description="Lista os embeds.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listarembeds(self, interaction: discord.Interaction):

        embeds = self.db_execute(
            "SELECT id, title FROM embeds WHERE guild_id=%s",
            (interaction.guild.id,),
            fetchall=True
        )

        if not embeds:
            await interaction.response.send_message("Nenhum embed criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{e[0]}` - {e[1]}" for e in embeds])

        await interaction.response.send_message(f"📄 **Embeds:**\n{lista}")

    @embed.command(name="deletar", description="Deleta um embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def deletarembed(self, interaction: discord.Interaction, id: int):

        self.db_execute(
            "DELETE FROM embeds WHERE id=%s AND guild_id=%s",
            (id, interaction.guild.id)
        )

        await interaction.response.send_message(f"🗑️ Embed `{id}` deletado.")

    @embed.command(name="enviar", description="Envia um embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enviarembed(self, interaction: discord.Interaction, id: int):

        result = self.db_execute("""
            SELECT title, description, color, image
            FROM embeds
            WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id), fetchone=True)

        if not result:
            await interaction.response.send_message("❌ Embed não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=result[0],
            description=result[1],
            color=result[2]
        )

        if result[3]:
            embed.set_image(url=result[3])

        await interaction.response.send_message(embed=embed)

    # ========================
    # RECADOS
    # ========================

    @recado.command(name="criar", description="Agenda um recado diário")
    @app_commands.checks.has_permissions(administrator=True)
    async def criar_recado(self, interaction: discord.Interaction, embed_id: int, horario: str, canal: discord.TextChannel):

        try:
            datetime.datetime.strptime(horario, "%H:%M")
        except ValueError:
            await interaction.response.send_message(
                "❌ Use formato HH:MM (ex: 12:30)",
                ephemeral=True
            )
            return

        self.db_execute("""
            INSERT INTO reminders (guild_id, channel_id, embed_id, horario)
            VALUES (%s, %s, %s, %s)
        """, (
            interaction.guild.id,
            canal.id,
            embed_id,
            horario
        ))

        await interaction.response.send_message(
            f"✅ Recado agendado para **{horario}**"
        )

    @recado.command(name="listar", description="Lista os recados")
    @app_commands.checks.has_permissions(administrator=True)
    async def recados(self, interaction: discord.Interaction):

        recados = self.db_execute("""
            SELECT id, embed_id, horario, channel_id
            FROM reminders
            WHERE guild_id=%s
            ORDER BY horario
        """, (interaction.guild.id,), fetchall=True)

        if not recados:
            await interaction.response.send_message("Nenhum recado.", ephemeral=True)
            return

        texto = "\n".join([
            f"ID `{r[0]}` • Embed `{r[1]}` • {r[2]} • <#{r[3]}>"
            for r in recados
        ])

        embed = discord.Embed(
            title="📢 Recados",
            description=texto,
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed)

    @recado.command(name="deletar", description="Deleta um recado")
    @app_commands.checks.has_permissions(administrator=True)
    async def recado_deletar(self, interaction: discord.Interaction, id: int):

        self.db_execute(
            "DELETE FROM reminders WHERE id=%s AND guild_id=%s",
            (id, interaction.guild.id)
        )

        await interaction.response.send_message(f"🗑️ Recado `{id}` deletado.")

    @recado.command(name="editar", description="Edita um recado")
    @app_commands.checks.has_permissions(administrator=True)
    async def recado_editar(self, interaction: discord.Interaction, id: int, novo_horario: str = None, novo_embed: int = None):

        recado = self.db_execute("""
            SELECT embed_id, horario
            FROM reminders
            WHERE id=%s AND guild_id=%s
        """, (id, interaction.guild.id), fetchone=True)

        if not recado:
            await interaction.response.send_message("❌ Recado não encontrado.", ephemeral=True)
            return

        embed_id = novo_embed or recado[0]
        horario = novo_horario or recado[1]

        self.db_execute("""
            UPDATE reminders
            SET embed_id=%s, horario=%s
            WHERE id=%s AND guild_id=%s
        """, (embed_id, horario, id, interaction.guild.id))

        await interaction.response.send_message(
            f"✅ Recado `{id}` atualizado para **{horario}**"
        )

    # ========================
    # ERROS
    # ========================
    async def cog_app_command_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Você precisa ser **admin** pra usar isso 😡",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Comandos(bot))
