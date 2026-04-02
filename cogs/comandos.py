# cogs/comandos.py
import discord
from discord import app_commands
from discord.ext import commands
import datetime
from database import get_connection

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    async def cog_load(self):
        self.pool = await get_connection()  # Usa o pool asyncpg

    embed = app_commands.Group(name="embeds", description="Comandos de embeds")
    recado = app_commands.Group(name="recado", description="Comandos de recados")

    # -------------------- CRIAR EMBED --------------------
    @embed.command(name="criar", description="Cria um embed padrão.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarembed(self, interaction: discord.Interaction):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO embeds (guild_id, title, description, color, image)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, interaction.guild.id, "Título do Embed", "Descrição padrão", 0x3498db, None)
            embed_id = row["id"]

        embed = discord.Embed(
            title="Título do Embed",
            description="Descrição padrão",
            color=0x3498db
        )
        await interaction.response.send_message(f"Embed criado com ID `{embed_id}`", embed=embed)

    # -------------------- EDITAR EMBED --------------------
    @embed.command(name="editar", description="Edita um embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def editarembed(self, interaction: discord.Interaction, id: int, novo_titulo: str = None, novo_descricao: str = None, nova_cor: int = None, imagem_url: str = None):
        async with self.pool.acquire() as conn:
            embed_data = await conn.fetchrow("SELECT title, description, color, image FROM embeds WHERE id=$1 AND guild_id=$2", id, interaction.guild.id)
            if not embed_data:
                await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
                return

            title = novo_titulo or embed_data["title"]
            description = novo_descricao or embed_data["description"]
            color = nova_cor or embed_data["color"]
            image = imagem_url or embed_data["image"]

            await conn.execute("""
                UPDATE embeds
                SET title=$1, description=$2, color=$3, image=$4
                WHERE id=$5 AND guild_id=$6
            """, title, description, color, image, id, interaction.guild.id)

        embed = discord.Embed(title=title, description=description, color=color)
        if image:
            embed.set_image(url=image)
        await interaction.response.send_message("Embed atualizado:", embed=embed)

    # -------------------- LISTAR EMBEDS --------------------
    @embed.command(name="listar", description="Lista os embeds.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listarembeds(self, interaction: discord.Interaction):
        async with self.pool.acquire() as conn:
            embeds = await conn.fetch("SELECT id, title FROM embeds WHERE guild_id=$1", interaction.guild.id)

        if not embeds:
            await interaction.response.send_message("Nenhum embed criado.", ephemeral=True)
            return

        lista = "\n".join([f"ID `{e['id']}` - {e['title']}" for e in embeds])
        await interaction.response.send_message(f"**Embeds:**\n{lista}")

    # -------------------- DELETAR EMBED --------------------
    @embed.command(name="deletar", description="Deleta um embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def deletarembed(self, interaction: discord.Interaction, id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM embeds WHERE id=$1 AND guild_id=$2", id, interaction.guild.id)
        await interaction.response.send_message(f"Embed `{id}` deletado.")

    # -------------------- ENVIAR EMBED --------------------
    @embed.command(name="enviar", description="Envia um embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enviarembed(self, interaction: discord.Interaction, id: int):
        async with self.pool.acquire() as conn:
            resultado = await conn.fetchrow("SELECT title, description, color, image FROM embeds WHERE id=$1 AND guild_id=$2", id, interaction.guild.id)

        if not resultado:
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        embed = discord.Embed(title=resultado["title"], description=resultado["description"], color=resultado["color"])
        if resultado["image"]:
            embed.set_image(url=resultado["image"])
        await interaction.response.send_message(embed=embed)

    # -------------------- CRIAR RECADOS --------------------
    @recado.command(name="criar", description="Agenda um recado diário")
    @app_commands.describe(embed_id="ID do embed", horario="Horário (HH:MM)", canal="Canal onde o recado será enviado")
    @app_commands.checks.has_permissions(administrator=True)
    async def criar_recado(self, interaction: discord.Interaction, embed_id: int, horario: str, canal: discord.TextChannel):
        try:
            datetime.datetime.strptime(horario, "%H:%M")
        except ValueError:
            await interaction.response.send_message("❌ Horário inválido. Use o formato `HH:MM`.", ephemeral=True)
            return

        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO reminders (guild_id, channel_id, embed_id, horario) VALUES ($1, $2, $3, $4)", interaction.guild.id, canal.id, embed_id, horario)

        await interaction.response.send_message(f"✅ Recado agendado para **{horario}** todos os dias.")

    # -------------------- LISTAR RECADOS --------------------
    @recado.command(name="listar", description="Lista os recados agendados")
    @app_commands.checks.has_permissions(administrator=True)
    async def recados(self, interaction: discord.Interaction):
        async with self.pool.acquire() as conn:
            recados = await conn.fetch("SELECT id, embed_id, horario, channel_id FROM reminders WHERE guild_id=$1 ORDER BY horario", interaction.guild.id)

        if not recados:
            await interaction.response.send_message("Nenhum recado agendado.", ephemeral=True)
            return

        texto = "".join([f"ID `{r['id']}` • Embed `{r['embed_id']}` • {r['horario']} • <#{r['channel_id']}>\n" for r in recados])
        embed = discord.Embed(title="📢 Recados agendados", description=texto, color=0x2ecc71)
        await interaction.response.send_message(embed=embed)

    # -------------------- DELETAR RECADOS --------------------
    @recado.command(name="deletar", description="Deleta um recado")
    @app_commands.checks.has_permissions(administrator=True)
    async def recado_deletar(self, interaction: discord.Interaction, id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM reminders WHERE id=$1 AND guild_id=$2", id, interaction.guild.id)
        await interaction.response.send_message(f"🗑️ Recado `{id}` deletado.")

    # -------------------- EDITAR RECADOS --------------------
    @recado.command(name="editar", description="Edita um recado")
    @app_commands.checks.has_permissions(administrator=True)
    async def recado_editar(self, interaction: discord.Interaction, id: int, novo_horario: str = None, novo_embed: int = None):
        async with self.pool.acquire() as conn:
            recado = await conn.fetchrow("SELECT embed_id, horario FROM reminders WHERE id=$1 AND guild_id=$2", id, interaction.guild.id)
            if not recado:
                await interaction.response.send_message("Recado não encontrado.", ephemeral=True)
                return

            embed_id = novo_embed or recado["embed_id"]
            horario = novo_horario or recado["horario"]

            await conn.execute("UPDATE reminders SET embed_id=$1, horario=$2 WHERE id=$3 AND guild_id=$4", embed_id, horario, id, interaction.guild.id)

        await interaction.response.send_message(f"✅ Recado `{id}` atualizado para **{horario}**.")

    # -------------------- ERROS --------------------
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Você precisa ser **administrador** para usar esse comando. ta achando que a vida é um murango é?? >:(",
                ephemeral=True
            )

# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Comandos(bot))