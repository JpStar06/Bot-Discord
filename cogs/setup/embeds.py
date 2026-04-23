import discord

def tutorial():
    embed = discord.Embed(
        title="📌 Bem-vindo ao tutorial da Aiko!",
        description=(
            "Aqui você vai aprender a usar o sistema de tickets, embeds e economia da Aiko "
            "de forma simples e rápida.\n\n"
            "Prometo que tudo será fácil de entender, então vamos lá! :3"
        ),
        color=discord.Color.pink()
    )

    return embed

def tutorial_embed():
    embed2 = discord.Embed(
        title="🎫 Sistema de Tickets",
        description=(
            "O sistema de tickets da Aiko é simples, intuitivo e eficiente.\n"
            "Ele permite que membros criem tickets para suporte enquanto a staff gerencia tudo facilmente.\n\n"
            "📌 Quando um ticket é fechado, um **transcript** é enviado para o usuário e a equipe."
        ),
        color=discord.Color.pink()
    )

    # Criar ticket
    embed2.add_field(
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
    embed2.add_field(
        name="📤 Enviando o painel",
        value=(
            "`/tickets enviar <id> <canal>`\n\n"
            "Envia o painel de ticket para o canal desejado."
        ),
        inline=False
    )

    # Interface
    embed2.add_field(
        name="✨ Interface",
        value=(
            "O sistema utiliza botões para abrir, fechar e editar tickets,\n"
            "tornando tudo mais prático e intuitivo."
        ),
        inline=False
    )

    embed2.set_footer(text="Aiko • Sistema de Tickets")

    return embed2

def tutorial_embed2():
    embed3 = discord.Embed(
        title="📋 Sistema de Embeds",
        description=(
            "O sistema de embeds da Aiko é simples, intuitivo e eficiente.\n"
            "Ele permite que membros criem embeds personalizados para comunicação com os usuários.\n\n"
            "📌 Os embeds podem conter título, descrição, cor, imagens e campos personalizados."
        ),
        color=discord.Color.pink()
    )
    
    embed3.add_field(
        name="🛠️ Como criar um embed",
        value=(
            "`/embeds criar` → cria um embed padrão\n"
            "`/embeds editar <id>` → personaliza o embed\n\n"
            "**Você pode alterar:**\n"
            "• Título\n"
            "• Descrição\n"
            "• Cor\n"
            "• Imagem"
        ),
        inline=False
    )

    embed3.add_field(
        name="📤 Enviando o embed",
        value=(
            "`/embeds enviar <id> <canal>`\n\n"
            "Envia o embed para o canal desejado."
        ),
        inline=False
    )
    embed3.add_field(
        name="✨ Interface",
        value=(
            "O sistema utiliza botões para editar os embeds,\n"
            "tornando tudo mais prático e intuitivo."
        ),
        inline=False
    )

    embed3.set_footer(text="Aiko • Sistema de Embeds")

    return embed3