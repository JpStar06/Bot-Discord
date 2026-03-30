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
    # UTIL (THREAD SAFE)
    # ========================
    async def db_execute(self, query, params=(), fetchone=False, fetchall=False):
        loop = self.bot.loop

        def run():
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)

                    if fetchone:
                        return cursor.fetchone()
                    if fetchall:
                        return cursor.fetchall()

                    conn.commit()

        return await loop.run_in_executor(None, run)

    # ========================
    # EMBEDS
    # ========================

    @embed.command(name="criar")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarembed(self, interaction: discord.Interaction):

        result = await self.db_execute("""
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
            f"✅ Embed criado (ID `{embed_id}`)",
            embed=embed
        )

    @embed.command(name="enviar")
    async def enviarembed(self, interaction: discord.Interaction, id: int):

        result = await self.db_execute("""
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

    @recado.command(name="criar")
    async def criar_recado(
        self,
        interaction: discord.Interaction,
        embed_id: int,
        horario: str,
        canal: discord.TextChannel
    ):

        # validar horário
        try:
            datetime.datetime.strptime(horario, "%H:%M")
        except ValueError:
            await interaction.response.send_message(
                "❌ Use HH:MM",
                ephemeral=True
            )
            return

        # validar embed
        exists = await self.db_execute(
            "SELECT id FROM embeds WHERE id=%s AND guild_id=%s",
            (embed_id, interaction.guild.id),
            fetchone=True
        )

        if not exists:
            await interaction.response.send_message(
                "❌ Esse embed não existe.",
                ephemeral=True
            )
            return

        await self.db_execute("""
            INSERT INTO reminders (guild_id, channel_id, embed_id, horario)
            VALUES (%s, %s, %s, %s)
        """, (
            interaction.guild.id,
            canal.id,
            embed_id,
            horario
        ))

        await interaction.response.send_message(
            f"⏰ Recado criado para {horario}"
        )

    # ========================
    # LISTAR RECADOS
    # ========================

    @recado.command(name="listar")
    async def recados(self, interaction: discord.Interaction):

        recados = await self.db_execute("""
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

    # ========================
    # ERROS
    # ========================

    async def cog_app_command_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.MissingPermissions):
            msg = "❌ Você precisa ser admin 😡"
        else:
            msg = f"⚠️ Erro: {error}"

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Comandos(bot))
