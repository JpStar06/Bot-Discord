import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔹 CRIAR EMBED
    @app_commands.command(name="criarembed", description="Cria um embed padrão.")
    async def criarembed(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id
        pasta = f"embeds/{guild_id}"

        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivos = [a for a in os.listdir(pasta) if a.startswith("embed_")]

        numero = max(
            [int(a.replace("embed_", "").replace(".json", "")) for a in arquivos],
            default=0
        ) + 1

        nome_arquivo = f"embed_{numero}.json"

        dados = {
            "title": "Título do Embed",
            "description": "Descrição padrão",
            "color": 0x3498db,
            "fields": [],
            "imagem": None
        }

        with open(f"{pasta}/{nome_arquivo}", "w") as f:
            json.dump(dados, f, indent=4)

        embed = discord.Embed(
            title=dados["title"],
            description=dados["description"],
            color=dados["color"],
        )

        if dados["imagem"]:
            embed.set_image(url=dados["imagem"])

        await interaction.response.send_message(
            f"Embed criado com ID `{numero}`",
            embed=embed
        )

    # 🔹 EDITAR EMBED
    @app_commands.command(name="editarembed", description="Edita um embed.")
    @app_commands.describe(
        id="ID do embed",
        novo_titulo="Novo título",
        novo_descricao="Nova descrição",
        nova_cor="Nova cor (decimal)",
        imagem_url="URL da imagem"
    )
    async def editarembed(
        self,
        interaction: discord.Interaction,
        id: int,
        novo_titulo: str,
        novo_descricao: str = None,
        nova_cor: int = None,
        imagem_url: str = None
    ):

        guild_id = interaction.guild.id
        nome_arquivo = f"embeds/{guild_id}/embed_{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        with open(nome_arquivo, "r") as f:
            dados = json.load(f)

        dados["title"] = novo_titulo

        if novo_descricao:
            dados["description"] = novo_descricao

        if nova_cor:
            dados["color"] = nova_cor

        if imagem_url:
            dados["imagem"] = imagem_url

        with open(nome_arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        embed = discord.Embed(
            title=dados["title"],
            description=dados["description"],
            color=dados["color"]
        )

        if dados["imagem"]:
            embed.set_image(url=dados["imagem"])

        await interaction.response.send_message("Embed atualizado:", embed=embed)

    # 🔹 LISTAR EMBEDS
    @app_commands.command(name="listarembeds", description="Lista os embeds criados.")
    async def listarembeds(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id
        pasta = f"embeds/{guild_id}"

        if not os.path.exists(pasta):
            await interaction.response.send_message("Nenhum embed criado ainda.", ephemeral=True)
            return

        arquivos = [a for a in os.listdir(pasta) if a.startswith("embed_")]

        if not arquivos:
            await interaction.response.send_message("Nenhum embed criado ainda.", ephemeral=True)
            return

        lista_embeds = []

        for arquivo in arquivos:
            with open(f"{pasta}/{arquivo}", "r") as f:
                dados = json.load(f)

            id = arquivo.split("_")[1].split(".")[0]
            lista_embeds.append(f"ID: `{id}` - Título: `{dados['title']}`")

        resposta = "\n".join(lista_embeds)

        await interaction.response.send_message(f"**Embeds Criados:**\n{resposta}")

    # 🔹 DELETAR EMBED
    @app_commands.command(name="deletarembed", description="Deleta um embed pelo ID.")
    @app_commands.describe(id="ID do embed a ser deletado")
    async def deletarembed(self, interaction: discord.Interaction, id: int):

        guild_id = interaction.guild.id
        nome_arquivo = f"embeds/{guild_id}/embed_{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        os.remove(nome_arquivo)

        await interaction.response.send_message(f"Embed com ID `{id}` deletado com sucesso.")

    # 🔹 ENVIAR EMBED
    @app_commands.command(name="enviarembed", description="Envia um embed para o canal.")
    @app_commands.describe(id="ID do embed a ser enviado")
    async def enviarembed(self, interaction: discord.Interaction, id: int):

        guild_id = interaction.guild.id
        nome_arquivo = f"embeds/{guild_id}/embed_{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        with open(nome_arquivo, "r") as f:
            dados = json.load(f)

        embed = discord.Embed(
            title=dados["title"],
            description=dados["description"],
            color=dados["color"]
        )

        if dados["imagem"]:
            embed.set_image(url=dados["imagem"])

        for field in dados["fields"]:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False)
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Comandos(bot))
