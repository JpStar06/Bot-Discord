import discord
from cogs.ticket.services import TicketService
from cogs.ticket.embeds import TicketEmbed

class EditPanelView(discord.ui.View):

    def __init__(self, data, ticket_id, guild_id):
        super().__init__(timeout=None)
        self.data = data
        self.ticket_id = ticket_id
        self.guild_id = guild_id

    async def update_message(self, interaction):
        embed = TicketEmbed.painel(self.data)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Título", style=discord.ButtonStyle.primary)
    async def titulo(self, interaction, button):
        from cogs.ticket.modals import EditTitleModal
        await interaction.response.send_modal(EditTitleModal(self))

    @discord.ui.button(label="Descrição", style=discord.ButtonStyle.secondary)
    async def desc(self, interaction, button):
        from cogs.ticket.modals import EditDescriptionModal
        await interaction.response.send_modal(EditDescriptionModal(self))

    @discord.ui.button(label="Cor", style=discord.ButtonStyle.success)
    async def cor(self, interaction, button):
        from cogs.ticket.modals import EditColorModal
        await interaction.response.send_modal(EditColorModal(self))

    @discord.ui.button(label="Imagem", style=discord.ButtonStyle.secondary)
    async def img(self, interaction, button):
        from cogs.ticket.modals import EditImageModal
        await interaction.response.send_modal(EditImageModal(self))

    @discord.ui.button(label="Salvar", style=discord.ButtonStyle.success)
    async def salvar(self, interaction, button):
        await TicketService.update_panel(self.guild_id, self.ticket_id, self.data)
        await interaction.response.send_message("✅ Salvo!", ephemeral=True)


class TicketView(discord.ui.View):

    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="abrir_ticket")
    async def abrir(self, interaction, button):

        await interaction.response.defer(ephemeral=True)

        thread, data = await TicketService.create_thread(
            interaction,
            self.ticket_id,
            interaction.user
        )

        if not thread:
            await interaction.followup.send(data, ephemeral=True)
            return

        embed = TicketEmbed.topico(data)

        staff_mention = ""
        if data.get("staff_id"):
            role = interaction.guild.get_role(data["staff_id"])
            if role:
                staff_mention = role.mention

        await thread.send(
            content=f"{interaction.user.mention} {staff_mention}",
            embed=embed
        )

        await interaction.followup.send(f"🎫 {thread.mention}", ephemeral=True)