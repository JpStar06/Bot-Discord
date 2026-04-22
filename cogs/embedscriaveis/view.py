import discord
from .modals import TitleModal, DescModal, ColorModal, ImageModal
from . import services

class EmbedBuilderView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=300)
        self.author = author

        self.title = "Título"
        self.description = "Descrição"
        self.color = discord.Color.blue()
        self.image = None

    def build_embed(self):
        embed = discord.Embed(title=self.title, description=self.description, color=self.color)
        if self.image:
            embed.set_image(url=self.image)
        return embed

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.author

    # 🔘 BOTÕES ↓↓↓

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

    @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.green)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):

        await services.editar_embed(interaction.guild.id, self.embed_id, self.title, self.description, self.color, self.image)

        await interaction.response.send_message(f"✏️ Embed `{self.embed_id}` atualizado!", ephemeral=True)