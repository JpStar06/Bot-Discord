import discord

class EditTitleModal(discord.ui.Modal, title="Editar Título"):

    def __init__(self, view):
        super().__init__()
        self.view = view

        self.titulo = discord.ui.TextInput(
            label="Título",
            default=view.data.get("titulo")
        )

        self.add_item(self.titulo)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["titulo"] = self.titulo.value
        await self.view.update_message(interaction)


class EditDescriptionModal(discord.ui.Modal, title="Editar Descrição"):

    def __init__(self, view):
        super().__init__()
        self.view = view

        self.desc = discord.ui.TextInput(
            label="Descrição",
            style=discord.TextStyle.paragraph,
            default=view.data.get("descricao")
        )

        self.add_item(self.desc)

    async def on_submit(self, interaction):
        self.view.data["descricao"] = self.desc.value
        await self.view.update_message(interaction)


class EditColorModal(discord.ui.Modal, title="Editar Cor"):

    def __init__(self, view):
        super().__init__()
        self.view = view

        self.cor = discord.ui.TextInput(
            label="Cor (hex)",
            default=str(view.data.get("cor"))
        )

        self.add_item(self.cor)

    async def on_submit(self, interaction):
        try:
            self.view.data["cor"] = int(self.cor.value, 16)
        except:
            self.view.data["cor"] = int(self.cor.value)

        await self.view.update_message(interaction)


class EditImageModal(discord.ui.Modal, title="Editar Imagem"):

    def __init__(self, view):
        super().__init__()
        self.view = view

        self.img = discord.ui.TextInput(
            label="URL da imagem",
            required=False,
            default=view.data.get("imagem")
        )

        self.add_item(self.img)

    async def on_submit(self, interaction):
        self.view.data["imagem"] = self.img.value or None
        await self.view.update_message(interaction)