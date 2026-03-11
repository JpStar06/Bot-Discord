import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="criarticket", description="um painel de tickets.")
    async def criarticket(self, interaction: discord.Interaction):
        
        guild_id = interaction.guild.id
        pasta = f"tickets/{guild_id}"

        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivos = os.listdir(pasta)
        numero = len(arquivos) + 1
        nome_arquivo = f"ticket{numero}.json"

        dados = {
            "painel_1": {
                "titulo": "Suporte",
                "descricao": "Clique no botão abaixo para abrir um ticket de suporte.",
                "cor": 0x3498db,
                "emoji": "🎫",
                "canal_id": None,
                "staff_id": None,
                "imagem": None
            }
        }
        with open(f"{pasta}/{nome_arquivo}", "w") as f:
            json.dump(dados, f, indent=4)
        embed = discord.Embed(
            title=dados["painel_1"]["titulo"],
            description=dados["painel_1"]["descricao"],
            color=dados["painel_1"]["cor"]
        )
        if dados["painel_1"]["imagem"]:
            embed.set_image(url=dados["painel_1"]["imagem"])

        view = discord.ui.View()
        button = discord.ui.Button(label="Abrir Ticket", emoji=dados["painel_1"]["emoji"], style=discord.ButtonStyle.primary, custom_id=f"abrir_ticket_{numero}")
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="listartickets", description="Lista os tickets criados.")
    async def listartickets(self, interaction: discord.Interaction):
        if not os.path.exists("tickets"):
            await interaction.response.send_message("Nenhum ticket criado ainda.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        pasta = f"tickets/{guild_id}"

        if not os.path.exists(pasta):
            await interaction.response.send_message("Nenhum ticket criado ainda.", ephemeral=True)
            return

        arquivos = os.listdir(pasta)
        lista_tickets = []
        for arquivo in arquivos:
            with open(f"{pasta}/{arquivo}", "r") as f:
                dados = json.load(f)
                id = arquivo.split(".")[0]
                lista_tickets.append(f"ID: `{id}` - Título: `{dados['painel_1']['titulo']}`")
        resposta = "\n".join(lista_tickets)
        await interaction.response.send_message(f"**Tickets Criados:**\n{resposta}")
            
    @app_commands.command(name="deletarticket", description="Deleta um ticket pelo ID.")
    @app_commands.describe(id="ID do ticket a ser deletado")
    async def deletarticket(self, interaction: discord.Interaction, id: int):
        guild_id = interaction.guild.id
        nome_arquivo = f"tickets/{guild_id}/ticket{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        os.remove(nome_arquivo)
        await interaction.response.send_message(f"Ticket com ID `{id}` deletado com sucesso.")

    @app_commands.command(name="editarticket", description="Edita o título de um ticket.")
    @app_commands.describe(id="ID do ticket a ser editado", novo_titulo="Novo título do ticket", nova_descricao="Nova descrição do ticket", nova_cor="Nova cor do ticket (em hexadecimal)", novo_emoji="Novo emoji do ticket", novo_canal_id="Novo ID do canal do ticket", novo_staff_id="Novo ID do staff do ticket", nova_imagem="Nova imagem do ticket")
    
    async def editarticket(self, interaction: discord.Interaction, id: int, novo_titulo: str = None, nova_descricao: str = None, nova_cor: int = None, novo_emoji: str = None, novo_canal_id: int = 
    None, novo_staff_id: int = None, nova_imagem: str = None):
    
        guild_id = interaction.guild.id
        nome_arquivo = f"tickets/{guild_id}/ticket{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        with open(nome_arquivo, "r") as f:
            dados = json.load(f)

        if novo_titulo:
            dados["painel_1"]["titulo"] = novo_titulo

        if nova_descricao:
            dados["painel_1"]["descricao"] = nova_descricao

        if nova_cor:
            dados["painel_1"]["cor"] = nova_cor

        if novo_emoji:
            dados["painel_1"]["emoji"] = novo_emoji

        if novo_canal_id:
            dados["painel_1"]["canal_id"] = novo_canal_id

        if novo_staff_id:
            dados["painel_1"]["staff_id"] = novo_staff_id

        if nova_imagem:
            dados["painel_1"]["imagem"] = nova_imagem

        with open(nome_arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        await interaction.response.send_message(f"Ticket com ID `{id}` editado com sucesso.")

    @app_commands.command(name="enviarticket", description="Envia o painel de ticket para o canal.")
    @app_commands.describe(id="ID do ticket a ser enviado")
    async def enviarticket(self, interaction: discord.Interaction, id: int):
        guild_id = interaction.guild.id
        pasta = f"tickets/{guild_id}"
        nome_arquivo = f"{pasta}/ticket{id}.json"

        if not os.path.exists(nome_arquivo):
            await interaction.response.send_message("Ticket não encontrado.", ephemeral=True)
            return

        with open(nome_arquivo, "r") as f:
            dados = json.load(f)

        embed = discord.Embed(
            title=dados["painel_1"]["titulo"],
            description=dados["painel_1"]["descricao"],
            color=dados["painel_1"]["cor"]
        )
        if dados["painel_1"]["imagem"]:
            embed.set_image(url=dados["painel_1"]["imagem"])

        view = discord.ui.View()
        button = discord.ui.Button(label="Abrir Ticket", emoji=dados["painel_1"]["emoji"], style=discord.ButtonStyle.primary, custom_id=f"abrir_ticket_{id}")
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):

        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")

        if not custom_id:
            return

        if custom_id.startswith("abrir_ticket_"):

            id_ticket = custom_id.split("_")[-1]

            guild_id = interaction.guild.id
            nome_arquivo = f"tickets/{guild_id}/ticket{id_ticket}.json"

            if not os.path.exists(nome_arquivo):
                await interaction.response.send_message(
                    "Configuração do ticket não encontrada.",
                    ephemeral=True
                )
                return

            with open(nome_arquivo) as f:
                dados = json.load(f)

            categoria_id = dados["painel_1"]["canal_id"]
            staff_id = dados["painel_1"]["staff_id"]

            categoria = interaction.guild.get_channel(int(categoria_id)) if categoria_id else None

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            if staff_id:
                staff_role = interaction.guild.get_role(int(staff_id))
                if staff_role:
                    overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

            canal = await interaction.guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=categoria,
                overwrites=overwrites
            )

            await interaction.response.send_message(
                f"🎫 Ticket criado: {canal.mention}",
                ephemeral=True
            )

            await canal.send(
                f"{interaction.user.mention} abriu um ticket.\nAguarde a equipe."
            )


async def setup(bot):
    await bot.add_cog(Tickets(bot))