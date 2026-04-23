import discord

def tutorial_embed():
    embed = discord.Embed(
        title="📌 Bem-vindo ao tutorial da Aiko!",
        description=(
            "Aqui você vai aprender a usar o sistema de tickets, embeds e economia da Aiko "
            "de forma simples e rápida.\n\n"
            "Prometo que tudo será fácil de entender, então vamos lá! :3"
        ),
        color=discord.Color.pink()
    )

    # Sistema de tickets
    embed.add_field(
        name="🎫 Sistema de Tickets",
        value=(
            "O sistema de tickets da Aiko é simples, intuitivo e eficiente.\n"
            "Ele permite que membros criem tickets para suporte enquanto a staff gerencia tudo facilmente.\n\n"
            "📌 Quando um ticket é fechado, um **transcript** é enviado para o usuário e a equipe."
        ),
        inline=False
    )

    # Criar ticket
    embed.add_field(
        name="🛠️ Como criar um ticket",
        value=(
            "`/tickets criar` → cria um ticket padrão\n"
            "`/tickets editar <id>` → personaliza o ticket\n\n"
            "**Você pode alterar:**\n"
            "• Título\n"
            "• Descrição\n"
            "• Cor\n"
            "• Cargo responsável\n"
            "• Imagem"
        ),
        inline=False
    )

    # Enviar painel
    embed.add_field(
        name="📤 Enviando o painel",
        value=(
            "`/tickets enviar <id> <canal>`\n\n"
            "Envia o painel de ticket para o canal desejado."
        ),
        inline=False
    )

    # Interface
    embed.add_field(
        name="✨ Interface",
        value=(
            "O sistema utiliza botões para abrir, fechar e editar tickets,\n"
            "tornando tudo mais prático e intuitivo."
        ),
        inline=False
    )

    embed.set_footer(text="Aiko • Sistema de Tickets")

    return embed