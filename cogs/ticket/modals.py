import re

import discord
from cogs.ticket.embeds import TicketEmbed
from cogs.ticket.view import EditPanelView, EditTopicView


class EditPanelModal(discord.ui.Modal, title="Editar Painel"):

    def __init__(self, data, ticket_id, guild_id):
        super().__init__()

        self.ticket_id = ticket_id
        self.guild_id = guild_id
        self.data = dict(data)

        self.titulo = discord.ui.TextInput(
            label="Título",
            default=data["titulo"],
        )
        self.descricao = discord.ui.TextInput(
            label="Descrição",
            style=discord.TextStyle.paragraph,
            default=data["descricao"],
        )
        self.cor = discord.ui.TextInput(
            label="Cor (hex ou int)",
            default=str(data["cor"]),
        )
        self.imagem = discord.ui.TextInput(
            label="URL da imagem",
            required=False,
            default=data.get("imagem"),
        )

        self.add_item(self.titulo)
        self.add_item(self.descricao)
        self.add_item(self.cor)
        self.add_item(self.imagem)

    async def on_submit(self, interaction: discord.Interaction):
        self.data.update({
            "titulo": self.titulo.value,
            "descricao": self.descricao.value,
            "cor": int(self.cor.value, 0),
            "imagem": self.imagem.value or None,
        })

        embed = TicketEmbed.painel(self.data)
        view = EditPanelView(self.data, self.ticket_id, self.guild_id)

        await interaction.response.send_message(
            content="👀 Pré-visualização:",
            embed=embed,
            view=view,
            ephemeral=True,
        )


class EditTopicModal(discord.ui.Modal, title="Editar Tópico do Ticket"):

    def __init__(self, data, ticket_id, guild_id):
        super().__init__()

        self.data = dict(data)
        self.ticket_id = ticket_id
        self.guild_id = guild_id

        self.staff = discord.ui.TextInput(
            label="Cargo Staff",
            placeholder="Nome do cargo (ex: adm) ou ID numérico",
            required=False,
            default=str(data.get("staff_id") or ""),
        )
        self.titulo = discord.ui.TextInput(
            label="Título",
            default=data["titulo_cliente"],
        )
        self.descricao = discord.ui.TextInput(
            label="Descrição",
            style=discord.TextStyle.paragraph,
            default=data["descricao_cliente"],
        )
        self.cor = discord.ui.TextInput(
            label="Cor (int ou hex)",
            default=str(data["cor_cliente"]),
        )
        self.imagem = discord.ui.TextInput(
            label="URL da imagem",
            required=False,
            default=data.get("imagem_cliente"),
        )

        self.add_item(self.titulo)
        self.add_item(self.descricao)
        self.add_item(self.cor)
        self.add_item(self.imagem)
        self.add_item(self.staff)

    async def on_submit(self, interaction: discord.Interaction):
        staff_id = None
        valor = self.staff.value.strip().lstrip("@")

        if valor:
            if valor.isdigit():
                # Usuário colou o ID numérico direto
                staff_id = int(valor)
            else:
                # Busca o cargo pelo nome no servidor
                role = discord.utils.find(
                    lambda r: r.name.lower() == valor.lower(),
                    interaction.guild.roles,
                )
                if role:
                    staff_id = role.id
                else:
                    await interaction.response.send_message(
                        f"❌ Cargo `{valor}` não encontrado no servidor. Verifique o nome e tente novamente.",
                        ephemeral=True,
                    )
                    return

        self.data.update({
            "titulo_cliente": self.titulo.value,
            "descricao_cliente": self.descricao.value,
            "cor_cliente": int(self.cor.value, 0),
            "imagem_cliente": self.imagem.value or None,
            "staff_id": staff_id,
        })

        embed = TicketEmbed.topico(self.data)
        view = EditTopicView(self.data, self.ticket_id, self.guild_id)

        await interaction.response.send_message(
            content="👀 Pré-visualização do tópico:",
            embed=embed,
            view=view,
            ephemeral=True,
        )
