import discord
from .modals import TitleModal, DescModal, ColorModal, ImageModal
from . import services
from .modals import StaffModal


class TicketBuilderView(discord.ui.View):
    def __init__(self, author, ticket_id: int):
        super().__init__(timeout=None)  # permanente

        self.author = author
        self.ticket_id = ticket_id
        self.staff_role = None
        self.staff_id = None

        self.title = "Título"
        self.description = "Descrição"
        self.color = discord.Color.blue()
        self.image = None

    def build_embed(self):
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )

        if self.image:
            embed.set_image(url=self.image)

        return embed

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "❌ Você não pode usar isso.",
                ephemeral=True
            )
            return False
        return True

    # -------- BOTÕES -------- #

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

        try:
            await services.editar_ticket(
                interaction.guild.id,
                self.ticket_id,
                self.title,
                self.description,
                self.color.value,  # 👈 correto
                self.image
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
    
    @discord.ui.button(label="👮 Atendente", style=discord.ButtonStyle.secondary)
    async def editar_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffModal(self))

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎫 Abrir Ticket",
        style=discord.ButtonStyle.green,
        custom_id="ticket_open_private"
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        # ⚠️ evita duplicar ticket
        for channel in guild.text_channels:
            if channel.name == f"ticket-{user.id}":
                return await interaction.response.send_message(
                    f"❌ Você já tem um ticket aberto: {channel.mention}",
                    ephemeral=True
                )

        # 👮 cargo de staff (troca pelo nome do seu cargo)
        staff_role = discord.utils.get(guild.roles, name="Staff")

        # 📁 categoria (cria se não existir)
        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")

        # 🔒 permissões
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        try:
            # 📦 cria canal
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}".replace(" ", "-").lower(),
                category=category,
                overwrites=overwrites
            )

            await channel.send(
                f"{user.mention} 🎫 Ticket criado!\nAguarde o suporte."
            )

            await interaction.response.send_message(
                f"✅ Seu ticket foi criado: {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao criar ticket: {e}",
                ephemeral=True
            )