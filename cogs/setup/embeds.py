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
            "`/embeds enviar <id> <canal>`\n"
            "Envia o embed para o canal desejado.\n\n"
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

def tutorial_embed3():
    embed4 = discord.Embed(
        title="💰 Sistema de Economia",
        description=(
            "O sistema de economia da Aiko é simples, intuitivo e eficiente.\n"
            "Ele permite que membros ganhem moedas virtuais através de atividades no servidor e as utilizem em recompensas personalizadas.\n\n"
            "📌 Os membros podem ganhar moedas jogando os minigames da Aiko! "
            "As moedas podem ser usadas livremente, seja para obter cargos com cores diferentes "
            "ou desbloquear conteúdos exclusivos. A escolha é totalmente sua. \nMas se lembre, é um pouco facil ganhar moedas, então coloque valores altos!"
            "\n\n ⚠️ **Aviso:** A Aiko não se responsabiliza por trocas, negociações ou acordos realizados entre membros. "
            "Fique atento a possíveis golpes e nunca compartilhe informações pessoais."
        ),
        color=discord.Color.pink()
    )
    embed4.add_field(
        name="💰 **Como ganhar moedas**",
        value=(
            "O sistema de economia da Aiko oferece várias formas de ganhar coins, seja trabalhando, coletando recompensas diárias ou testando sua sorte no casino.\n\n"
            "🪙 **Formas de ganhar coins:**\n"
            "• `/eco diario` → Colete sua recompensa diária e aumente seu streak 🔥\n"
            "• `/eco work` → Trabalhe e receba coins com base em um emprego aleatório\n"
            "• `/box abrir` → Abra lootboxes para ganhar recompensas\n"
            "• `/casino ...` → Use os jogos de aposta para tentar multiplicar suas moedas\n\n"
            "🎲 **Jogos de aposta:**\n"
            "• `/casino coinflip` → Escolha entre cara ou coroa\n"
            "• `/casino dice` → Role um dado contra o bot\n"
            "• `/casino slots` → Teste sua sorte no caça-níquel\n"
            "• `/casino blackjack` → Use estratégia para vencer o bot\n\n"

            "📌 **Outras funções úteis:**\n"
            "• `/eco carteira` → Veja suas coins, boxes e streak\n"
            "• `/eco pay` → Envie coins para outros membros\n"
            "• `/eco rank` → Veja os jogadores mais ricos do servidor\n"
            "• `/box comprar` → Compre lootboxes\n\n"

            "⏳ **Importante:**\n"
            "Alguns comandos possuem cooldown para evitar spam.\n"
            "Você só pode usar e apostar valores que possui.\n\n"

            "⚠️ **Dica:**\n"
            "Use suas coins com sabedoria — jogos de aposta podem tanto aumentar quanto diminuir seu saldo.\n"
            "Tente equilibrar entre sorte, estratégia e consistência para crescer na economia! :3"
        ),
        inline=False
    )

    embed4.set_footer(text="Aiko • Sistema de Economia")

    return embed4