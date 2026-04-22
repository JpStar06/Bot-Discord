import discord
from cogs.ticket.services import TicketService
from cogs.ticket.embeds import TicketEmbed
import asyncio

class EditPanelView(discord.ui.View):

    def __init__(self, data, ticket_id, guild_id):
        super().__init__(timeout=300)
        self.data = data
        self.ticket_id = ticket_id
        self.guild_id = guild_id

    @discord.ui.button(label="Salvar", style=discord.ButtonStyle.success)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):

        await TicketService.update_panel(
            self.guild_id,
            self.ticket_id,
            self.data
        )

        await interaction.response.send_message(
            "✅ Alterações salvas!",
            ephemeral=True
        )

class EditTopicView(discord.ui.View):

    def __init__(self, data, ticket_id, guild_id):
        super().__init__(timeout=None)
        self.data = data
        self.ticket_id = ticket_id
        self.guild_id = guild_id

    @discord.ui.button(label="Salvar", style=discord.ButtonStyle.success, custom_id="save_topic")
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("clicou")
        await TicketService.update_topic(
            self.guild_id,
            self.ticket_id,
            self.data
        )
        await interaction.response.send_message(
            "✅ Tópico salvo!",
            ephemeral=True
        )

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
            if role:
                staff_mention = role.mention
            else:
                staff_mention = f"⚠️ Cargo de staff (ID: {data['staff_id']}) não encontrado"
        else:
            staff_mention = "@here"   # ou "" se não quiser mencionar ninguém

        await thread.send(
            content=f"{interaction.user.mention} {staff_mention}",
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.followup.send(
            f"🎫 Ticket criado: {thread.mention}",
            ephemeral=True
        )

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
        except:
            pass