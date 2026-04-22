import discord


# ─────────────────────────────────────────────
#  MODAIS — PAINEL
# ─────────────────────────────────────────────

class PanelTituloModal(discord.ui.Modal, title="Editar Título do Painel"):
    novo_titulo = discord.ui.TextInput(label="Título")

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.novo_titulo.default = view.data.get("titulo")

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["titulo"] = self.novo_titulo.value
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class PanelDescricaoModal(discord.ui.Modal, title="Editar Descrição do Painel"):
    descricao = discord.ui.TextInput(
        label="Descrição",
        style=discord.TextStyle.paragraph
    )

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.descricao.default = view.data.get("descricao")

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["descricao"] = self.descricao.value
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class PanelCorModal(discord.ui.Modal, title="Editar Cor do Painel"):
    cor = discord.ui.TextInput(label="Cor (hex)", placeholder="#3498db")

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.cor.default = hex(view.data.get("cor", 0))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.view.data["cor"] = int(self.cor.value.replace("#", ""), 16)
        except ValueError:
            await interaction.response.send_message("❌ Cor inválida!", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class PanelImagemModal(discord.ui.Modal, title="Editar Imagem do Painel"):
    url = discord.ui.TextInput(
        label="URL da imagem",
        required=False,
        placeholder="https://..."
    )

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.url.default = view.data.get("imagem") or ""

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["imagem"] = self.url.value or None
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


# ─────────────────────────────────────────────
#  MODAIS — TÓPICO
# ─────────────────────────────────────────────

class TopicTituloModal(discord.ui.Modal, title="Editar Título do Tópico"):
    novo_titulo = discord.ui.TextInput(label="Título")

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.novo_titulo.default = view.data.get("titulo_cliente")

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["titulo_cliente"] = self.novo_titulo.value
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class TopicDescricaoModal(discord.ui.Modal, title="Editar Descrição do Tópico"):
    descricao = discord.ui.TextInput(
        label="Descrição",
        style=discord.TextStyle.paragraph
    )

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.descricao.default = view.data.get("descricao_cliente")

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["descricao_cliente"] = self.descricao.value
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class TopicCorModal(discord.ui.Modal, title="Editar Cor do Tópico"):
    cor = discord.ui.TextInput(label="Cor (hex)", placeholder="#ff0000")

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.cor.default = hex(view.data.get("cor_cliente", 0))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.view.data["cor_cliente"] = int(self.cor.value.replace("#", ""), 16)
        except ValueError:
            await interaction.response.send_message("❌ Cor inválida!", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class TopicImagemModal(discord.ui.Modal, title="Editar Imagem do Tópico"):
    url = discord.ui.TextInput(
        label="URL da imagem",
        required=False,
        placeholder="https://..."
    )

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.url.default = view.data.get("imagem_cliente") or ""

    async def on_submit(self, interaction: discord.Interaction):
        self.view.data["imagem_cliente"] = self.url.value or None
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class TopicStaffModal(discord.ui.Modal, title="Editar Cargo Staff"):
    staff = discord.ui.TextInput(
        label="Cargo Staff",
        placeholder="Nome do cargo (ex: adm) ou ID numérico",
        required=False
    )

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.staff.default = str(view.data.get("staff_id") or "")

    async def on_submit(self, interaction: discord.Interaction):
        valor = self.staff.value.strip().lstrip("@")
        staff_id = None

        if valor:
            if valor.isdigit():
                staff_id = int(valor)
            else:
                role = discord.utils.find(
                    lambda r: r.name.lower() == valor.lower(),
                    interaction.guild.roles
                )
                if role:
                    staff_id = role.id
                else:
                    await interaction.response.send_message(
                        f"❌ Cargo `{valor}` não encontrado no servidor.",
                        ephemeral=True
                    )
                    return

        self.view.data["staff_id"] = staff_id
        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )
