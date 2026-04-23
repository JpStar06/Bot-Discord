import discord
from discord import app_commands
from discord.ext import commands

class setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    @app_commands.command(name="setup", description="Configura o sistema do bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(interaction: discord.Interaction):

        guild = interaction.guild

        # 📁 cria canal se não existir
        channel = discord.utils.get(guild.text_channels, name="aiko-tuto")

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

        # 📘 embeds de tutorial

        embed1 = discord.Embed(
            title="🎫 Sistema de Tickets",
            description="Aprenda a usar o sistema de tickets do bot.",
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
            value="Use `/tickets enviar <id>`",
            inline=False
        )

        embed2 = discord.Embed(
            title="🎛 Editor de Ticket",
            description="Use os botões para configurar seu ticket:",
            color=discord.Color.green()
        )

        embed2.add_field(name="✏️ Título", value="Define o título", inline=True)
        embed2.add_field(name="📝 Descrição", value="Define o texto", inline=True)
        embed2.add_field(name="🎨 Cor", value="Cor do embed", inline=True)
        embed2.add_field(name="🖼️ Imagem", value="Imagem do ticket", inline=True)
        embed2.add_field(name="👮 Atendente", value="Cargo staff", inline=True)

        embed3 = discord.Embed(
            title="🎫 Como funciona o ticket",
            description=(
                "1. Usuário clica no botão\n"
                "2. Canal privado é criado\n"
                "3. Staff é notificado\n"
                "4. Ticket pode ser fechado com botão ❌"
            ),
            color=discord.Color.red()
        )

        # 🧹 limpa canal antes
        await channel.purge(limit=10)

        # 📩 envia tudo
        await channel.send(embed=embed1)
        await channel.send(embed=embed2)
        await channel.send(embed=embed3)

        await interaction.response.send_message(f"✅ Setup concluído em {channel.mention}")

async def setup(bot):
    await bot.add_cog(setup(bot))