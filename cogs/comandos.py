import discord
from discord import app_commands
from discord.ext import commands
from database import get_connection


class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # CRIAR EMBED
    @app_commands.command(name="criarembed", description="Cria um embed padrão.")
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
    @app_commands.command(name="editarembed", description="Edita um embed.")
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
    @app_commands.command(name="listarembeds", description="Lista os embeds.")
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
    @app_commands.command(name="deletarembed", description="Deleta um embed.")
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
    @app_commands.command(name="enviarembed", description="Envia um embed.")
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


async def setup(bot):
    await bot.add_cog(Comandos(bot))