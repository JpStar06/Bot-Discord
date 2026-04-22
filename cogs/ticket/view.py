import discord
import asyncio
from cogs.ticket.services import TicketService
from cogs.ticket.embeds import TicketEmbed
from cogs.ticket.modals import (
    PanelTituloModal, PanelDescricaoModal, PanelCorModal, PanelImagemModal,
    TopicTituloModal, TopicDescricaoModal, TopicCorModal, TopicImagemModal,
    TopicStaffModal,
)


# ─────────────────────────────────────────────
#  EDITAR PAINEL
# ─────────────────────────────────────────────

class EditPanelView(discord.ui.View):

    def __init__(self, data, ticket_id, guild_id, author):
        super().__init__(timeout=300)
        self.data = dict(data)
        self.ticket_id = ticket_id
        self.guild_id = guild_id
        self.author = author

    def build_embed(self):
        return TicketEmbed.painel(self.data)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.author

    @discord.ui.button(label="✏️ Título", style=discord.ButtonStyle.primary)
    async def editar_titulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PanelTituloModal(self))

    @discord.ui.button(label="📝 Descrição", style=discord.ButtonStyle.secondary)
    async def editar_descricao(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PanelDescricaoModal(self))

    @discord.ui.button(label="🎨 Cor", style=discord.ButtonStyle.success)
    async def editar_cor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PanelCorModal(self))

    @discord.ui.button(label="🖼️ Imagem", style=discord.ButtonStyle.secondary)
    async def editar_imagem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PanelImagemModal(self))

    @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.green, row=1)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await TicketService.update_panel(self.guild_id, self.ticket_id, self.data)
        await interaction.response.send_message("✅ Painel salvo!", ephemeral=True)


# ─────────────────────────────────────────────
#  EDITAR TÓPICO
# ─────────────────────────────────────────────

class EditTopicView(discord.ui.View):

    def __init__(self, data, ticket_id, guild_id, author):
        super().__init__(timeout=300)
        self.data = dict(data)
        self.ticket_id = ticket_id
        self.guild_id = guild_id
        self.author = author

    def build_embed(self):
        return TicketEmbed.topico(self.data)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.author

    @discord.ui.button(label="✏️ Título", style=discord.ButtonStyle.primary)
    async def editar_titulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopicTituloModal(self))

    @discord.ui.button(label="📝 Descrição", style=discord.ButtonStyle.secondary)
    async def editar_descricao(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopicDescricaoModal(self))

    @discord.ui.button(label="🎨 Cor", style=discord.ButtonStyle.success)
    async def editar_cor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopicCorModal(self))

    @discord.ui.button(label="🖼️ Imagem", style=discord.ButtonStyle.secondary)
    async def editar_imagem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopicImagemModal(self))

    @discord.ui.button(label="👮 Staff", style=discord.ButtonStyle.secondary)
    async def editar_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopicStaffModal(self))

    @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.green, row=1)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await TicketService.update_topic(self.guild_id, self.ticket_id, self.data)
        await interaction.response.send_message("✅ Tópico salvo!", ephemeral=True)


# ─────────────────────────────────────────────
#  TICKET VIEW (botão de abrir ticket no canal)
# ─────────────────────────────────────────────

class TicketView(discord.ui.View):

    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(
        label="Abrir Ticket",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="abrir_ticket"
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        thread, data = await TicketService.create_thread(
            interaction,
            self.ticket_id,
            interaction.user
        )

        if not thread:
            await interaction.followup.send(f"Erro: {data}", ephemeral=True)
            return

        embed = TicketEmbed.topico(data)
        staff_mention = ""

        if data.get("staff_id"):
            role = interaction.guild.get_role(data["staff_id"])
            staff_mention = role.mention if role else f"⚠️ Cargo de staff (ID: {data['staff_id']}) não encontrado"
        else:
            staff_mention = "@here"

        await thread.send(
            content=f"{interaction.user.mention} {staff_mention}",
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.followup.send(
            f"🎫 Ticket criado: {thread.mention}",
            ephemeral=True
        )


# ─────────────────────────────────────────────
#  FECHAR TICKET
# ─────────────────────────────────────────────

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Fechar Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="fechar_ticket"
    )
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔒 Fechando em 5 segundos...",
            ephemeral=True
        )
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception:
            pass
