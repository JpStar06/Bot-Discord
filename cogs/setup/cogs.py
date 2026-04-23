import discord
from discord.ext import commands
from discord import app_commands


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configura o sistema do bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild

        # 📁 procurar canal
        channel = discord.utils.get(guild.text_channels, name="aiko-tuto")

        # 📁 criar se não existir
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False
                )
            }

            channel = await guild.create_text_channel(
                name="aiko-tuto",
                overwrites=overwrites
            )

        # 🧹 limpar mensagens antigas
        try:
            await channel.purge(limit=20)
        except:
            pass

        # 📘 EMBED 1
        embed1 = discord.Embed(
            title="🎫 Sistema de Tickets",
            description="Aprenda a usar o sistema de tickets.",
            color=discord.Color.blue()
        )

        embed1.add_field(
            name="🛠 Criar ticket",
            value="Use `/tickets criar`",
            inline=False
        )

        embed1.add_field(
            name="✏️ Editar ticket",
            value="Use `/tickets editar <id>`",
            inline=False
        )

        embed1.add_field(
            name="📤 Enviar ticket",
            value="Use `/tickets enviar <id_tickets><id_canal>`",
            inline=False
        )

        # 📘 EMBED 2
        embed2 = discord.Embed(
            title="🎛 Editor de Ticket",
            description="Use os botões para configurar:",
            color=discord.Color.green()
        )

        embed2.add_field(name="✏️ Título", value="Define o título", inline=True)
        embed2.add_field(name="📝 Descrição", value="Define o texto", inline=True)
        embed2.add_field(name="🎨 Cor", value="Cor do embed", inline=True)
        embed2.add_field(name="🖼️ Imagem", value="Imagem do ticket", inline=True)
        embed2.add_field(name="👮 Atendente", value="Cargo staff", inline=True)

        # 📘 EMBED 3
        embed3 = discord.Embed(
            title="🎫 Como funciona",
            description=(
                "1. Clique no botão 🎫\n"
                "2. Canal privado será criado\n"
                "3. Staff será notificado\n"
                "4. Use ❌ para fechar"
            ),
            color=discord.Color.red()
        )

        # 📩 enviar
        await channel.send(embed=embed1)
        await channel.send(embed=embed2)
        await channel.send(embed=embed3)

        await interaction.followup.send(
            f"✅ Setup concluído em {channel.mention}",
            ephemeral=True
        )


# 🔧 loader obrigatório (NÃO MUDA)
async def setup(bot):
    await bot.add_cog(SetupCog(bot))