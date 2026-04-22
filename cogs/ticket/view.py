import discord
from .modals import (
    TitleModal,
    DescModal,
    ColorModal,
    ImageModal,
    StaffModal
)
from . import services


class TicketBuilderView(discord.ui.View):
    def __init__(self, author, ticket_id: int):
        super().__init__(timeout=None)

        self.author = author
        self.ticket_id = ticket_id

        self.title = "Título"
        self.description = "Descrição"
        self.color = discord.Color.blue()
        self.image = None

        self.staff_role = None
        self.staff_id = None

    # -------------------- EMBED -------------------- #
    def build_embed(self):
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )

        if self.image:
            embed.set_image(url=self.image)

        if self.staff_role:
            embed.add_field(
                name="👮 Atendente",
                value=self.staff_role.mention,
                inline=False
            )

        return embed

    # -------------------- PERMISSÃO -------------------- #
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "❌ Você não pode usar isso.",
                ephemeral=True
            )
            return False
        return True

    # -------------------- BOTÕES -------------------- #

    @discord.ui.button(label="✏️ Título", style=discord.ButtonStyle.primary)
    async def editar_titulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TitleModal(self))

    @discord.ui.button(label="📝 Descrição", style=discord.ButtonStyle.secondary)
    async def editar_desc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DescModal(self))

    @discord.ui.button(label="🎨 Cor", style=discord.ButtonStyle.success)
    async def editar_cor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ColorModal(self))

    @discord.ui.button(label="🖼️ Imagem", style=discord.ButtonStyle.secondary)
    async def editar_img(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ImageModal(self))

    @discord.ui.button(label="👮 Atendente", style=discord.ButtonStyle.secondary)
    async def editar_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffModal(self))

    # -------------------- SALVAR -------------------- #
    @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.green)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("VIEW STAFF_ID:", self.staff_id)

        try:
            await services.editar_ticket(
                interaction.guild.id,
                self.ticket_id,
                self.title,
                self.description,
                self.color.value,  # 👈 salva como int
                self.image,
                self.staff_id  # 👈 salva staff
            )

            await interaction.response.send_message(
                f"✅ Ticket `{self.ticket_id}` atualizado!",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao salvar: {e}",
                ephemeral=True
            )