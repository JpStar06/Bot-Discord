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
    # DATABASE (ASYNC - NEON)
    # ========================
    async def db_execute(self, query, *params, fetchone=False, fetchall=False):
        pool = await get_connection()

        async with pool.acquire() as conn:

            if fetchone:
                return await conn.fetchrow(query, *params)

            if fetchall:
                return await conn.fetch(query, *params)

            await conn.execute(query, *params)

    # ========================
    # EMBEDS
    # ========================

    @embed.command(name="criar", description="Cria um embed padrão.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarembed(self, interaction: discord.Interaction):

        result = await self.db_execute("""
            INSERT INTO embeds (guild_id, title, description, color, image)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            interaction.guild.id,
            "Título do Embed",
            "Descrição padrão",
            0x3498db,
            None,
            fetchone=True
        )

        embed_id = result["id"]

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

        data = await self.db_execute("""
            SELECT title, description, color, image
            FROM embeds
            WHERE id=$1 AND guild_id=$2
        """, id, interaction.guild.id, fetchone=True)

        if not data:
            await interaction.response.send_message("❌ Embed não encontrado.", ephemeral=True)
            return

        title = novo_titulo
        description = novo_descricao or data["description"]
        color = nova_cor or data["color"]
        image = imagem_url or data["image"]

        await self.db_execute("""
            UPDATE embeds
            SET title=$1, description=$2, color=$3, image=$4
            WHERE id=$5 AND guild_id=$6
        """, title, description, color, image, id, interaction.guild.id)

        embed = discord.Embed(title=title, description=description, color=color)

        if image:
            embed.set_image(url=image)

        await interaction.response.send_message("✅ Embed atualizado:", embed=embed)

    @embed.command(name="listar", description="Lista os embeds.")
    async def listarembeds(self, interaction: discord.Interaction):

        embeds = await self.db_execute("""
            SELECT id, title FROM embeds WHERE guild_id=$1
        """, interaction.guild.id, fetchall=True)

        if not embeds:
            await interaction.response.send_message("Nenhum embed criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{e['id']}` - {e['title']}" for e in embeds])

        await interaction.response.send_message(f"📄 **Embeds:**\n{lista}")

    @embed.command(name="deletar", description="Deleta um embed.")
    async def deletarembed(self, interaction: discord.Interaction, id: int):

        await self.db_execute(
            "DELETE FROM embeds WHERE id=$1 AND guild_id=$2",
            id, interaction.guild.id
        )

        await interaction.response.send_message(f"🗑️ Embed `{id}` deletado.")

    @embed.command(name="enviar", description="Envia um embed.")
    async def enviarembed(self, interaction: discord.Interaction, id: int):

        result = await self.db_execute("""
            SELECT title, description, color, image
            FROM embeds
            WHERE id=$1 AND guild_id=$2
        """, id, interaction.guild.id, fetchone=True)

        if not result:
            await interaction.response.send_message("❌ Embed não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(
            title=result["title"],
            description=result["description"],
            color=result["color"]
        )

        if result["image"]:
            embed.set_image(url=result["image"])

        await interaction.response.send_message(embed=embed)

    # ========================
    # RECADOS
    # ========================

    @recado.command(name="criar", description="Agenda um recado diário")
    async def criar_recado(self, interaction: discord.Interaction, embed_id: int, horario: str, canal: discord.TextChannel):

        try:
            datetime.datetime.strptime(horario, "%H:%M")
        except ValueError:
            await interaction.response.send_message("❌ Use HH:MM", ephemeral=True)
            return

        exists = await self.db_execute(
            "SELECT id FROM embeds WHERE id=$1 AND guild_id=$2",
            embed_id, interaction.guild.id,
            fetchone=True
        )

        if not exists:
            await interaction.response.send_message("❌ Esse embed não existe.", ephemeral=True)
            return

        await self.db_execute("""
            INSERT INTO reminders (guild_id, channel_id, embed_id, horario)
            VALUES ($1, $2, $3, $4)
        """, interaction.guild.id, canal.id, embed_id, horario)

        await interaction.response.send_message(f"⏰ Recado agendado para {horario}")

    @recado.command(name="listar", description="Lista os recados")
    async def recados(self, interaction: discord.Interaction):

        recados = await self.db_execute("""
            SELECT id, embed_id, horario, channel_id
            FROM reminders
            WHERE guild_id=$1
            ORDER BY horario
        """, interaction.guild.id, fetchall=True)

        if not recados:
            await interaction.response.send_message("Nenhum recado.", ephemeral=True)
            return

        texto = "\n".join([
            f"ID `{r['id']}` • Embed `{r['embed_id']}` • {r['horario']} • <#{r['channel_id']}>"
            for r in recados
        ])

        embed = discord.Embed(
            title="📢 Recados",
            description=texto,
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed)

    @recado.command(name="deletar", description="Deleta um recado")
    async def recado_deletar(self, interaction: discord.Interaction, id: int):

        await self.db_execute(
            "DELETE FROM reminders WHERE id=$1 AND guild_id=$2",
            id, interaction.guild.id
        )

        await interaction.response.send_message(f"🗑️ Recado `{id}` deletado.")

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
