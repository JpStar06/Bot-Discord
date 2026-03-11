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

        # cria pasta se não existir
        if not os.path.exists("embeds"):
            os.makedirs("embeds")

        # gera próximo ID automaticamente
        arquivos = os.listdir("embeds")
        numero = len(arquivos) + 1
        nome_arquivo = f"embeds/embed_{numero}.json"

        dados = {
            "title": "Título do Embed",
            "description": "Descrição padrão",
            "color": 0x3498db,
            "fields": [],
            "imagem": None
        }

        with open(nome_arquivo, "w") as f:
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

        nome_arquivo = f"embeds/embed_{id}.json"

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
    
    @app_commands.command(name="listarembeds", description="Lista os embeds criados.")
    async def listarembeds(self, interaction: discord.Interaction):
        if not os.path.exists("embeds"):
            await interaction.response.send_message("Nenhum embed criado ainda.", ephemeral=True)
            return

        arquivos = os.listdir("embeds")
        if not arquivos:
            await interaction.response.send_message("Nenhum embed criado ainda.", ephemeral=True)
            return

        lista_embeds = []
        for arquivo in arquivos:
            with open(f"embeds/{arquivo}", "r") as f:
                dados = json.load(f)
                id = arquivo.split("_")[1].split(".")[0]
                lista_embeds.append(f"ID: `{id}` - Título: `{dados['title']}`")

        resposta = "\n".join(lista_embeds)
        await interaction.response.send_message(f"**Embeds Criados:**\n{resposta}")

    @app_commands.command(name="deletarembed", description="Deleta um embed pelo ID.")
    @app_commands.describe(id="ID do embed a ser deletado")
    async def deletarembed(self, interaction: discord.Interaction, id: int):
        nome_arquivo = f"embeds/embed_{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        os.remove(nome_arquivo)
        await interaction.response.send_message(f"Embed com ID `{id}` deletado com sucesso.")

    @app_commands.command(name="enviarembed", description="Envia um embed para o canal.")
    @app_commands.describe(id="ID do embed a ser enviado")
    async def enviarembed(self, interaction: discord.Interaction, id: int):
        nome_arquivo = f"embeds/embed_{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Embed não encontrado.", ephemeral=True)
            return

        with open(nome_arquivo, "r") as f:
            dados = json.load(f)

        embed = discord.Embed(
            title=dados["title"],
            description=dados["description"],
            color=dados["color"],
        )
        if dados["imagem"]:
            embed.set_image(url=dados["imagem"])

        for field in dados["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Comandos(bot))